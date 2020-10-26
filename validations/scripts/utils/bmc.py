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
from scripts.utils.common import run_subprocess_cmd
from scripts.utils.pillar_get import PillarGet
from messages.user_messages import *

logger = logging.getLogger(__name__)

class BMC():

    def __init__(self):
        """ Validations for BMC steps
        """
        pass

    def get_bmc_ip(self):
        """ Get BMC IP along with status of command
        """
        common_response = {}
        bmc_ip = []

        node_res = PillarGet.get_pillar("cluster:node_list")
        if node_res['ret_code']:
            return node_res

        nodes = node_res['response']
        for node in nodes:
            bmc_ip_get = PillarGet.get_pillar(f"cluster:{node}:bmc:ip")
            if bmc_ip_get['ret_code']:
                return bmc_ip_get
            bmc_ip.append(bmc_ip_get["response"])

        common_response["response"] = bmc_ip
        common_response["ret_code"]= node_res["ret_code"]
        common_response["error_msg"]= node_res["error_msg"]
        return common_response

    def get_bmc_power_status(self):
        """ Get BMC Power Status
        """
        logger.info("Get BMC Power Status")

        cmd = "ipmitool chassis status | grep 'System Power'"
        res = run_subprocess_cmd(cmd)
        return {
            'ret_code': res[0],
            'response': res[1],
            'error_msg': res[2],
            'message':''
        }
