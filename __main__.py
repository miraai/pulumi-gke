from pulumi import Config, export, get_project, get_stack, ResourceOptions
from pulumi_kubernetes import Provider
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.core.v1 import ContainerArgs, PodSpecArgs, PodTemplateSpecArgs, Service, ServicePortArgs, ServiceSpecArgs
from pulumi_kubernetes.meta.v1 import LabelSelectorArgs, ObjectMetaArgs

from infrastracture.kubernetes import create_gke_cluster

config = Config(None)

NODE_COUNT = config.get_int("node_count", default=1)
# NODE_MACHINE_TYPE is a machine type to use for cluster nodes.
NODE_MACHINE_TYPE = config.get("node_machine_type", default="n1-standard-1")
# Master version of GKE engine.
MASTER_VERSION = config.get("master_version")

kubeconfig = create_gke_cluster(resource_name="gke-cluster", initial_node_count=NODE_COUNT, node_version=MASTER_VERSION, node_machine_type=NODE_MACHINE_TYPE)

# Create Kubernetes provider instance that uses the cluster ^^^^^
k8s_provider = Provider("gke_k8s", kubeconfig=kubeconfig)

labels = {"app": f"nginx-{get_project()}-{get_stack()}"}
nginx = Deployment("nginx",
    spec=DeploymentSpecArgs(
        selector=LabelSelectorArgs(match_labels=labels),
        replicas=1,
        template=PodTemplateSpecArgs(
            metadata=ObjectMetaArgs(labels=labels),
            spec=PodSpecArgs(containers=[ContainerArgs(name="nginx", image="nginx")]),
        ),
    ), opts=ResourceOptions(provider=k8s_provider)
)

ingress = Service("nginx",
    spec=ServiceSpecArgs(
        type="LoadBalancer",
        selector=labels,
        ports=[ServicePortArgs(port=80)],
    ), opts=ResourceOptions(provider=k8s_provider)
)

def get_load_balancer_ip(info):
    return info.load_balancer.ingress[0].ip

export("nginx_service_ip", ingress.status.apply(get_load_balancer_ip))