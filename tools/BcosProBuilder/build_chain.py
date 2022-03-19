#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
# Note: here can't be refactored by autopep
sys.path.append("src/")

import os
import toml
from networkmgr.network_manager import NetworkManager
from command.node_command_impl import NodeCommandImpl
from command.service_command_impl import ServiceCommandImpl
from controller.binary_controller import BinaryController
from config.chain_config import ChainConfig
from common.utilities import ServiceInfo
from common.utilities import CommandInfo
from common import parser_handler
from common import utilities


def chain_operations(args):
    if parser_handler.is_chain_command(args) is False:
        return
    if os.path.exists(args.config) is False:
        utilities.log_error("The config file '%s' not found!" % args.config)
        sys.exit(-1)
    toml_config = toml.load(args.config)
    chain_config = ChainConfig(toml_config)
    op_type = args.type
    if op_type not in ServiceInfo.supported_service_type:
        utilities.log_error("the service type must be " +
                            ', '.join(ServiceInfo.supported_service_type))
        return
    command = args.op
    if op_type == ServiceInfo.rpc_service_type or op_type == ServiceInfo.gateway_service_type:
        if command in CommandInfo.service_command_impl.keys():
            command_impl = ServiceCommandImpl(chain_config, args.type)
            impl_str = CommandInfo.service_command_impl[command]
            cmd_func_attr = getattr(command_impl, impl_str)
            cmd_func_attr()
            return
    if op_type == ServiceInfo.node_service_type:
        if command in CommandInfo.node_command_to_impl.keys():
            command_impl = NodeCommandImpl(chain_config)
            impl_str = CommandInfo.node_command_to_impl[command]
            cmd_func_attr = getattr(command_impl, impl_str)
            cmd_func_attr()
            return
    utilities.log_info("unimplemented command")


def create_subnet_operation(args):
    if parser_handler.is_create_subnet_command(args) is False:
        return
    docker_network_name = args.name
    if docker_network_name is None or len(docker_network_name) == 0:
        utilities.log_error(
            "Must set the docker network name! e.g. tars-network")
        sys.exit(-1)
    subnet_ip_segment = args.subnet
    if subnet_ip_segment is None or len(subnet_ip_segment) == 0:
        utilities.log_error("Must set the subnet! e.g. 172.25.0.0.1")
        sys.exist(-1)
    NetworkManager.create_sub_net(subnet_ip_segment, docker_network_name)
    utilities.print_split_info()


def add_vxlan_operation(args):
    if parser_handler.is_add_vxlan_command(args) is False:
        return
    utilities.print_split_info()
    network = args.network
    if network is None or len(network) == 0:
        utilities.log_error(
            "Must set a valid non-empty network name, e.g. tars-network")
        return
    dstip = args.dstip
    if dstip is None or len(dstip) == 0:
        utilities.log_error("Must set a valid non-empty dst ip")
        return
    vxlan_name = args.vxlan
    if vxlan_name is None or len(vxlan_name) == 0:
        utilities.log_error("Must set a valid non-empty vxlan name")
        return
    NetworkManager.create_bridge(network, vxlan_name, dstip)
    utilities.print_split_info()


def download_binary_operation(args):
    if parser_handler.is_download_binary_command(args) is False:
        return
    utilities.print_split_info()
    binary_path = args.path
    version = args.version
    if version.startswith("v") is False:
        version = "v" + version
    if args.type not in CommandInfo.download_type:
        utilities.log_error("Unsupported download type %s, only support %s now" % (
            args.type, ', '.join(CommandInfo.download_type)))
        return
    use_cdn = True
    if args.type == "git":
        use_cdn = False
    binary_controller = BinaryController(version, binary_path, use_cdn)
    binary_controller.download_all_binary()
    utilities.print_split_info()


def main():
    args = parser_handler.parse_command()
    chain_operations(args)
    create_subnet_operation(args)
    add_vxlan_operation(args)
    download_binary_operation(args)


if __name__ == "__main__":
    main()
