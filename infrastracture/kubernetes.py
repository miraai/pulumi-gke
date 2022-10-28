from pulumi import export, Output
from pulumi_gcp.config import project
from pulumi_gcp.container import Cluster, ClusterNodeConfigArgs
from pulumi_kubernetes import Provider

from infrastracture.consts import CLUSTER_NODE_OAUTH_SCOPES, DEFAULT_LOCATION
from infrastracture.kubeconfig import KUBECONFIG


def create_gke_cluster(
  resource_name,
  initial_node_count,
  node_version,
  node_machine_type,
  min_master_version = None,
  location = DEFAULT_LOCATION,
):
    if not min_master_version:
        min_master_version = node_version

    # Create GKE cluster.
    k8s_cluster = Cluster(
        resource_name=resource_name,
        location=location,
        initial_node_count=initial_node_count, 
        node_version=node_version,
        min_master_version=min_master_version, 
        node_config=ClusterNodeConfigArgs(
            machine_type=node_machine_type,
            # OAuth scopes for nodes to be able to reach Google API.
            oauth_scopes=CLUSTER_NODE_OAUTH_SCOPES
        ),
    )

    # Output data needed for k8s_config.
    k8s_info = Output.all(k8s_cluster.name, k8s_cluster.location, k8s_cluster.endpoint, k8s_cluster.master_auth)

    # Create Kubeconfig
    # apply takes output values and passes them to the called func (lambda)
    k8s_config = k8s_info.apply(
        lambda info: KUBECONFIG.format(
        cluster_certificate=info[3]['cluster_ca_certificate'],
        endpoint=info[2],
        cluster_slug=f"{project}_{info[1]}_{info[0]}"
      )
    )

    export("kubeconfig", k8s_config)

    return k8s_config