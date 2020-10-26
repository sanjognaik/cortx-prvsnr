#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

import logging
from messages.user_messages import *
import subprocess
from scripts.utils.bmc import BMC
from scripts.utils.network_connectivity_checks import NetworkValidations

from scripts.utils.common import *

logger = logging.getLogger(__name__)

class BMCValidations():

    def __init__(self):
        """ Validations for BMC steps
        """
        self.bmc = BMC()
        self.nw_conn = NetworkValidations()

    def ping_bmc(self):
        """ Ping BMC IP
        """
        # TODO: Add check for ping BMC from another node
        logger.info("Ping BMC IP")

        response = {}
        res_ip_get = self.bmc.get_bmc_ip()
        if res_ip_get['ret_code']:
            return res_ip_get

        for ip in res_ip_get["response"]:
            ping_check = NetworkValidations.check_ping(ip)
            if ping_check['ret_code']:
                ping_check["message"]= str(BMC_PING_IP_ERROR)
                return ping_check

        response["ret_code"]= ping_check['ret_code']
        response["message"]= str(BMC_PING_IP_CHECK)
        response["response"]= ping_check["response"]
        response["error_msg"]= ping_check["error_msg"]
        return response

    def verify_bmc_power_status(self):
        """ Validations for BMC power status
        """
        # TODO: Add check for BMC power status from another node
        logger.info("verify_bmc_power_status check")

        response = self.bmc.get_bmc_power_status()
        if response['ret_code']:
            response['message'] = str(BMC_POWER_GET_ERROR)
            logger.error(response)
            return response

        if "on" in str(response['response']):
            response['message'] = str(BMC_POWER_CHECK)
            logger.debug(response)
        else:
            response['ret_code'] = 1
            response['message'] = str(BMC_POWER_ERROR)
            logger.error(response)

        return response

    def verify_bmc_accessible(self):
        """ Validations for BMC accessibility
        """
        # TODO: Add check for BMC accessibility from another node
        logger.info("verify_bmc_accessible check")

        response = self.verify_bmc_power_status()
        if response['ret_code']:
            return

        response = self.ping_bmc()
        if response['ret_code']:
            return

        response['message'] = "BMC is accessible from both nodes"
        logger.debug(response)
        return response

    def check_ssh(self):
        logger.info('Check SSH')
        respose = ssh_remote_machine('srvnode-2', 'root', 'seagate')
        return respose
