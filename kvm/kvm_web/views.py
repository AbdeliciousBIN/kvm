import uuid

from django.shortcuts import redirect, render
import sys
import libvirt
from .tasks import create_vm
import datetime

# Create your views here.
def index(request):
    return render (request,'index.html')

def ajoutKvm(request):
    if request.method=='POST':
        data= request.POST
        nameKvm = str(data.get('nameKvm'))
        memory = str(data.get('memory'))
        cpu = str(data.get('cpu'))
        os = str(data.get('os'))

        conn=libvirt.open("qemu:///system")
        domains=conn.listAllDomains(0)

        for domain in domains:
            if(domain.name()==nameKvm):
                errorExit0=True #VM NAME ALREADY EXIST 
                return render(request,'ajout.html',{'error0':errorExit0})

        if(create_vm(name=nameKvm,memory=memory,cpu=cpu,os=os)):
            return redirect('listeKvm')
        else:
            errorExit1=True
            return render(request,'listeKvm.html',{"error1":errorExit1})
    datetime_now = datetime.datetime.now()
    datetime_form= datetime_now.strftime("%Y-%m-%dT%H:%M:%S") #forwarding datetime.now() to form 
    print(datetime_form)
    return render(request,'ajout.html',{'datetime_form':datetime_form}) # Render Form of VM
        


#        xmlConf=''' <domain type='kvm'>
#                     <name>'''+nameKvm+'''</name>
#	                 <uuid>'''+str(uuid.uuid4())+'''</uuid>
#	                 <memory unit='KiB'>'''+memory+'''</memory>
#	                <vcpu>'''+cpu+'''</vcpu>
#	                <os>
#	            	<type arch='x86_64' machine='pc'>hvm</type>
# 		            <boot dev='hd'/>
# 		            <boot dev='cdrom'/>
#	                 </os>
#	                <clock offset='utc'/>
#	                <on_poweroff>destroy</on_poweroff>
#	                <on_reboot>restart</on_reboot>
#	                <on_crash>destroy</on_crash>
#	                <devices>
#	                  <emulator>/usr/bin/qemu-system-x86_64</emulator>
#	                 <disk type='file' device='disk'>
#	                  <source file='/var/lib/libvirt/images/demo.qcow2'/>
#	                 <driver name='qemu' type='raw'/>
#	                <target dev='hda'/>
#	                 </disk>
#	                    <disk type='file' device='cdrom'>
#  		            <source file='/home/estell/isoFiles/ubuntu-22.04-desktop-amd64.iso'/>
#  		            <target dev='hdc' bus='ide'/>
#		            </disk>
#	                <interface type='network'>
#	                 <source network='default'/>
#	                </interface>
#	                <input type='mouse' bus='ps2'/>
#	                 <graphics type='vnc' port='-1' listen='127.0.0.1'/>
#	                </devices>
#	                </domain> '''
        #
#        try:
#            dom=conn.defineXMLFlags(xmlConf,0)
#            dom.create()
#        except libvirt.libvirtError as e :
#            print(repr(e), file=sys.stderr)
#            errorExit1=True
#            return render(request,'listeKvm.html',{"error1":errorExit1})
#
#       return redirect('listeKvm')
    
    

def listeKvm(request):
    conn=libvirt.open("qemu:///system")
    domains = conn.listAllDomains(0) #If a value of 0 is specified then all domains will be listed.
    arrayName=[]
    arrayState=[]
    
    
    for domain in domains:
        
        arrayName.append(domain.name())
        arrayState.append(domain.state()) # return array of ['state','reason']
        
    arrayStateFiltred=[]
    for state in arrayState:
        if state[0] == libvirt.VIR_DOMAIN_RUNNING:
            arrayStateFiltred.append("RUNNING")
        elif state[0] == libvirt.VIR_DOMAIN_PAUSED:
            arrayStateFiltred.append("PAUSED")
        elif state[0] == libvirt.VIR_DOMAIN_SHUTDOWN:
            arrayStateFiltred.append("SHUTDOWN")
        elif state[0] == libvirt.VIR_DOMAIN_SHUTOFF:
            arrayStateFiltred.append("SHUTOFF")
        else:
            arrayStateFiltred.append("UNKOWN")

    zippedList = zip(arrayName, arrayStateFiltred)
    for item in arrayStateFiltred:	
        print(item)
    return render(request,'listeKvm.html',{"list":zippedList})


def start(request,name):
    conn=libvirt.open("qemu:///system")
    dom=conn.lookupByName(name)
    dom.create()
    return redirect('listeKvm')

def resume(requet,name):
    conn=libvirt.open("qemu:///system")
    dom=conn.lookupByName(name)
    dom.resume()
    return redirect('listeKvm')

def pause(request,name):
    conn=libvirt.open("qemu:///system")
    dom=conn.lookupByName(name)
    
    return redirect('listeKvm')

def shutdown(request,name):
    conn=libvirt.open("qemu:///system")
    dom=conn.lookupByName(name)
    dom.shutdown()
    return redirect('listeKvm')

def delete(request,name):
    conn=libvirt.open("qemu:///system")
    dom=conn.lookupByName(name)
    dom.undefine()
    return redirect('listeKvm')

def destroy(request,name):
    conn=libvirt.open("qemu:///system")
    dom=conn.lookupByName(name)
    dom.destroy()
    return redirect('listeKvm')