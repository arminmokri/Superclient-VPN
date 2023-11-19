import time
from threading import Thread
import logging
import sys

from superclient.action.models import ServiceStatus
from superclient.vpn.models import Configuration
from superclient.action.service.Router import Router
from superclient.setting.models import General
from superclient.subscription.models import SubscriptionConfig


def start():
    logging.info("start tasks...")
    TaskThread().start()


class TaskThread(Thread):

    start_delay = 5
    repeat_delay = 5
    counter = 0

    def run(self):

        try:
            time.sleep(self.start_delay)
            ServiceStatus.get().change_previous_vpn(None)
        except Exception as e:
            try:
                logging.error(e)
            except Exception as e:
                pass

        while True:
            try:

                time.sleep(self.repeat_delay)

                service_checker(self.counter, self.repeat_delay)

                if self.counter == sys.maxsize:
                    self.counter = 0
                else:
                    self.counter = self.counter + 1

            except Exception as e:
                try:
                    if self.counter == sys.maxsize:
                        self.counter = 0
                    else:
                        self.counter = self.counter + 1
                    logging.error(e)
                except Exception as e:
                    pass


def service_checker(counter, repeat_delay):
    status = ServiceStatus.get()

    logging.info("counter=" + str(counter) + ", repeat_delay=" + str(repeat_delay))

    if status.on:
        if status.active_vpn == None:
            start_vpn_service(status)
            status.change_previous_vpn(status.active_vpn)
        elif (
            status.active_vpn != None
            and status.selected_vpn != None
            and status.selected_vpn != status.active_vpn
        ):  # when change selected vpn
            logging.info("[CHANGE] selected vpn changed.")
            stop_vpn_service(status)
            status.change_previous_vpn(None)
        elif status.active_vpn != None and status.active_vpn not in list(
            Configuration.objects.filter(enable=True).all()
        ):  # when delete vpn or disable vpn
            logging.info("[CHANGE] selected vpn is disabled or deleted.")
            stop_vpn_service(status)
            status.change_previous_vpn(None)
        elif status.active_vpn != None and status.apply:  # when apply
            logging.info("[CHANGE] apply setting is called.")
            stop_vpn_service(status)
            status.change_previous_vpn(None)
            status.toggle_apply()
        elif (
            status.active_vpn != None
            and (counter * repeat_delay) % 10 == 0
            and not Router(status.active_vpn).is_running()
        ):  # when proc is not up
            logging.info("[CHANGE] vpn pid failed.")
            stop_vpn_service(status)
        elif (
            status.active_vpn != None
            and (counter * repeat_delay) % 60 == 0
            and not Router(status.active_vpn).check_vpn()
        ):  # when connection is week
            logging.info("[CHANGE] vpn check connection failed.")
            stop_vpn_service(status)
        else:
            logging.info("[NO-CHANGE] vpn service already started.")
    else:
        if status.active_vpn != None:  # when stop vpn
            logging.info("[CHANGE] apply stop is called.")
            stop_vpn_service(status)
            status.change_previous_vpn(None)
        elif status.apply:  # when apply
            status.change_previous_vpn(None)
            status.toggle_apply()
        else:
            logging.info("[NO-CHANGE] vpn service already stoped.")

    if (counter * repeat_delay) % 300 == 0:
        subscriptionConfigs = list(SubscriptionConfig.objects.filter(resync=True).all())
        for subscriptionConfig in subscriptionConfigs:
            if subscriptionConfig.subclass.update():
                subscriptionConfig.resync = False
                subscriptionConfig.save()


def start_vpn_service(status: ServiceStatus):
    logging.info("starting vpn...")

    general = General.objects.first()
    vpn_list = []
    if status.selected_vpn == None:
        if general.vpn_smart_mode == general.VpnSmartMode.success_chance:
            logging.info("will use auto select vpn strategy in success chance mode.")
            vpn_list = list(Configuration.objects.filter(enable=True).all())
            vpn_list.sort(reverse=True, key=success_chance)
        elif general.vpn_smart_mode == general.VpnSmartMode.priority:
            logging.info("will use auto select vpn strategy in priority mode...")
            vpn_list = list(
                Configuration.objects.filter(enable=True).order_by("-priority").all()
            )
        elif general.vpn_smart_mode == general.VpnSmartMode.circular:
            logging.info("will use auto select vpn strategy in circular mode.")
            vpn_list = list(
                Configuration.objects.filter(enable=True).order_by("id").all()
            )

        if status.previous_active_vpn != None:
            index = vpn_list.index(status.previous_active_vpn)
            vpn_list = (
                vpn_list[index + 1 :] + vpn_list[:index] + vpn_list[index : index + 1]
            )
    else:
        logging.info("will use static vpn strategy...")
        vpn_list.append(status.selected_vpn)

    i = 0
    vpn_str = "vpn list ["
    for vpn in vpn_list:
        vpn_str = vpn_str + "({}) {} ".format(i, vpn.title)
        i = i + 1
    vpn_str = vpn_str + "]"
    logging.info(vpn_str)

    if len(vpn_list) == 0:
        logging.error("vpn not found.")
    else:
        for vpn in vpn_list:
            logging.info("try connect to vpn configuration {}.".format(vpn.title))
            router = Router(vpn)
            res, output = router.ConnectVPN(
                timeout_arg=general.timeout_of_try_for_each_vpn,
                try_count_arg=general.number_of_try_for_each_vpn,
            )
            vpn.add_log(output)
            if res == 0:
                vpn.increase_success()
                status.change_active_vpn(vpn)
                logging.info("vpn connected.")
                break
            else:
                vpn.increase_failed()
                status.change_active_vpn(None)
                logging.error("vpn connected failed.")
                continue


def stop_vpn_service(status: ServiceStatus):
    logging.info("stoping vpn...")
    if status.active_vpn != None:
        logging.info(
            "try disconnect vpn configuration {}.".format(status.active_vpn.title)
        )
        router = Router(status.active_vpn)
        res, output = router.DisconnectVPN()
        status.change_active_vpn(None)
        if res == 0:
            logging.info("vpn disconnected.")
        else:
            logging.error("vpn disconnected failed.")


def success_chance(key):
    return key.success_chance
