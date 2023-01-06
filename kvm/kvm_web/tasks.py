import uuid
from celery import shared_task
import libvirt 
import sys


@shared_task
def create_vm(name,memory,cpu,os):

    xmlConf=''' <domain type='kvm'>
                     <name>'''+name+'''</name>
	                 <uuid>'''+str(uuid.uuid4())+'''</uuid>
	                 <memory unit='KiB'>'''+memory+'''</memory>
	                <vcpu>'''+cpu+'''</vcpu>
	                <os>
	            	<type arch='x86_64' machine='pc'>hvm</type>
  		            <boot dev='hd'/>
 		            <boot dev='cdrom'/>
	                 </os>
	                <clock offset='utc'/>
	                <on_poweroff>destroy</on_poweroff>
	                <on_reboot>restart</on_reboot>
	                <on_crash>destroy</on_crash>
	                <devices>
	                  <emulator>/usr/bin/qemu-system-x86_64</emulator>
	                 <disk type='file' device='disk'>
	                  <source file='/var/lib/libvirt/images/demo.qcow2'/>
	                 <driver name='qemu' type='raw'/>
	                <target dev='hda'/>
	                 </disk>
	                    <disk type='file' device='cdrom'>
  		            <source file='/home/estell/isoFiles/ubuntu-22.04-desktop-amd64.iso'/>
  		            <target dev='hdc' bus='ide'/>
		            </disk>
	                <interface type='network'>
	                 <source network='default'/>
	                </interface>
	                <input type='mouse' bus='ps2'/>
	                 <graphics type='vnc' port='-1' listen='127.0.0.1'/>
	                </devices>
	                </domain> '''
    
    try:
            conn=libvirt.open("qemu:///system")
            dom=conn.defineXMLFlags(xmlConf,0)
            dom.create()
            
    except libvirt.libvirtError as e :
            print(repr(e), file=sys.stderr)
            return False #Failed creation of VM 
    return True #Success creation of VM 
