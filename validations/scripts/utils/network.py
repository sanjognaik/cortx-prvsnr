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
from scripts.utils.network_connectivity_checks  import NetworkValidations
from scripts.utils.common import run_subprocess_cmd
from messages.user_messages import *
from scripts.utils.pillar_get import PillarGet

logger = logging.getLogger(__name__)

class Network():

    def __init__(self):
        """ Initialize network class
        """
        self.nw = NetworkValidations()

    def get_ip_from_iface(self, iface):
        """ This function gets the IP from given interface.
        """

        logger.info(f"Get ip from dev : {iface}")

        response = {}
        pub_ip = None
        cmd = f"ip addr show dev {iface} | grep 'inet'"
        response = run_subprocess_cmd(cmd)

        if response['ret_code']:
            response['message'] = str(NW_DEVICE_DOES_NOT_EXIST).format(iface)
        else:
            if 'inet' in response['response']:
                pub_ip = response['response'].strip().split()[1].split('/')[0]
                response['response'] = pub_ip
                response['message'] = str(NW_IP_FOUND).format(pub_ip, iface)
            else:
                response['message'] = str(NW_IP_DEV_INVALID_OP)

        if response['ret_code']:
            logger.error(f"'{cmd}' : '{response['message']}'")
        else:
            logger.debug(f"'{cmd}' : '{response['message']}'")
        return response

    def verify_public_data_ip(self):
        """ This function checks if public data ip is configured successfully
            or not.
        """

        logger.info("verify_public_data_ip check")
        response = {}

        node_res = PillarGet.get_pillar("cluster:node_list")
        if node_res['ret_code']:
            return node_res

        nodes = node_res['response']
        for node in nodes:
            iface_resp = PillarGet.get_pillar(f"cluster:{node}:network:network:iface")
            if iface_resp['ret_code']:
                return iface_resp

            for ifc in iface_resp['response']:
                if 's0f0' in ifc:
                    # Get public data ip from interface
                    response = self.get_ip_from_iface(ifc)
                    if response['ret_code']:
                        return response

                    # Ping public data ip
                    response = self.nw.check_ping(response['response'])
                    if response['ret_code']:
                        return response

                    break

        response['message'] = str(NW_PUB_DATA_IP_SUCCESS)
        logger.debug(response['message'])
        return response
