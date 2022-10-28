KUBECONFIG = """apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {cluster_certificate}
    server: https://{endpoint}
  name: {cluster_slug}
contexts:
- context:
    cluster: {cluster_slug}
    user: {cluster_slug}
  name: {cluster_slug}
current-context: {cluster_slug}
kind: Config
preferences: {{}}
users:
- name: {cluster_slug}
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: gke-gcloud-auth-plugin
      installHint: Install gke-gcloud-auth-plugin for use with kubectl by following
        https://cloud.google.com/blog/products/containers-kubernetes/kubectl-auth-changes-in-gke
      provideClusterInfo: true
"""