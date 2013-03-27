import sys
import urllib.error
import urllib.request
from xml.dom import minidom

host = "localhost"
page = "mypagetotest"

test_args = {
    "Param1" : [ "Arg1", "Arg2", "Arg3" ],
    "Param1" : [ "Arg1", "Arg2", "Arg3" ] }

def getDocument(url):    
    content_handle = urllib.request.urlopen(url)                    
    return minidom.parseString(content_handle.read().decode("utf8"))        

def getServiceName(document):
    return document.getElementsByTagName("wsdl:service")[0].getAttribute("name")

def getTypes(document):    
    nodes = document.getElementsByTagName("s:schema")[0].childNodes    
    enums = {}
    elements = {}
    for node in nodes:
        if type(node) is minidom.Element:
            if node.tagName == "s:element":
                params = [(subNode.getAttribute("name"), subNode.getAttribute("type")) for subNode in node.getElementsByTagName("s:element")]                
                elements[node.getAttribute("name")] = params
            elif node.tagName == "s:simpleType":
                enumValues = [(subNode.getAttribute("name"), subNode.getAttribute("type")) for subNode in node.getElementsByTagName("s:enumeration")]
                enums[node.getAttribute("name")] = enumValues
    return (elements, enums)

def getTypeNames(document):    
    nodes = document.getElementsByTagName("s:schema")[0].childNodes    
    enums = {}
    elements = {}
    for node in nodes:
        if type(node) is minidom.Element:
            if node.tagName == "s:element":
                params = [subNode.getAttribute("name") for subNode in node.getElementsByTagName("s:element")]                
                elements[node.getAttribute("name")] = params
            elif node.tagName == "s:simpleType":
                enumValues = [subNode.getAttribute("name") for subNode in node.getElementsByTagName("s:enumeration")]
                enums[node.getAttribute("name")] = enumValues
    return (elements, enums)

def getOperations(document):
    service_name = document.getElementsByTagName("wsdl:service")[0].getAttribute("name")
    binding_name = service_name + "HttpGet"
    bindings = document.getElementsByTagName("wsdl:binding")
    for binding in bindings:
        if binding.getAttribute("name") == binding_name:
            return [binding.getAttribute("location")[1:] for binding in binding.getElementsByTagName("http:operation")]
    return []

def getOperationUrl(host, page, op, param_arg_pairs):
    return "http://{0}/{1}/{2}?{3}".format(host, page, op, "&".join(["=".join(param_arg_pair) for param_arg_pair in param_arg_pairs]))

def getPerms(params, args, perms, perm):    
    if len(args) == 1:        
        for i in range(0, len(args[0])):
            perms.append(perm + [(params[0], args[0][i])])        
    else:
        for i in range(0, len(args[0])):            
            getPerms(params[1:], args[1:], perms, perm + [(params[0], args[0][i])])    
    return perms
    
wsdDocument = getDocument("http://{0}/{1}?wsdl".format(host, page))
serviceName = getServiceName(wsdDocument)
elements, enums = getTypeNames(wsdDocument)
operations = getOperations(wsdDocument)

fout = open("wsdltester-{0}.log".format(serviceName), "w")

for op in operations:
    msg = "\nTesting {0} operation.".format(op)
    fout.write(msg)
    print(msg)
    args = [test_args[param] for param in elements[op]]    
    op_values = getPerms(elements[op], args, [], [])    
    for op_value in op_values:        
        op_url = getOperationUrl(host, page, op, op_value)
        msg = "GET {0}".format(op_url)
        print(msg)
        fout.write(msg)
        op_doc = getDocument(op_url)
        fout.write(op_doc.toprettyxml())        
        
        

