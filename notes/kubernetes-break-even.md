# Kubernetes has a break-even point

A working note on the argument in `kubernetes-break-even.json`. Written to clarify the thesis, the numbers behind it, and the nuances that did not make the deck.

## Thesis

Kubernetes is a general-purpose container orchestrator with real value and a large operational cost. The value scales with the number of services, the variability of load, and the maturity of the team. The cost is roughly fixed. There is a point on that curve where the two lines cross, and most teams are to the left of it.

The goal of the deck is to give someone a sharp, honest test for which side of the line they are on.

## What Kubernetes actually does

Four capabilities you would otherwise build and maintain yourself.

1. **Scheduling.** Places workloads across a fleet of nodes based on CPU, memory, and affinity rules.
2. **Self-healing.** Restarts failed containers, reschedules off dead nodes, gates traffic on health checks.
3. **Service networking.** Internal DNS, load balancing, and stable addressing for pods that come and go.
4. **Rollouts.** Declarative rolling updates with automatic rollback when health checks fail.

These are real primitives. If you tried to assemble them yourself from systemd, HAProxy, and a cron job, you would end up with a worse version of Kubernetes in 18 months.

## The complexity tax

The cost Kubernetes imposes on any team that adopts it.

- **Operational surface.** API server, etcd, scheduler, controller manager, kubelet, CNI, CSI, ingress. Each component has its own failure modes and its own debugging workflow.
- **Upgrade cadence.** Kubernetes ships three minor versions a year. Each version is supported for 14 months (12 months of standard support plus a 2 month upgrade window). Falling behind drops you out of the security patch window.
- **Abstraction debt.** Every primitive has a dozen knobs you will eventually need to tune in production. The defaults are reasonable until they are not.
- **Observability cost.** Cluster metrics, pod metrics, and application metrics are three separate systems you now own.

The tax is paid primarily in engineer-hours, not dollars. The EKS bill is cheap compared to the engineer who has to understand it.

## Three conditions under which the cost pays off

All three must hold. Any missing one pushes the break-even line away from you.

1. **Multi-service footprint.** You run 15 or more services that need to share infrastructure rather than each running on its own VM pool.
2. **Uneven traffic.** Load swings by 10x or more across the day, and paying for peak capacity around the clock is more expensive than autoscaling.
3. **High deployment velocity.** You ship to production several times a day across many services, and rolling updates with rollback are a first-class need.

The numbers are heuristics. The shape of the curve is what matters. A team with 4 services and flat traffic is clearly to the left. A team with 40 services and 20x daily load swings is clearly to the right.

## Three conditions under which the cost exceeds the benefit

Any one of these is enough to pick something simpler.

1. **Small service count.** Under five services. The control plane costs more to operate than the workloads it runs.
2. **Steady load.** Traffic is flat within a 2x range. Autoscaling is the main structural benefit, and flat traffic leaves it on the table.
3. **No unambiguous owner.** Nobody is the clear, deeply knowledgeable owner of the cluster. Shared ownership of distributed systems leaves outages that no one can debug.

## Alternatives to reach for first

Most teams land on one of these three and never need to look further.

| Option | Best for | Tradeoff |
|---|---|---|
| **ECS + Fargate** | AWS shops running under 20 services that want containers without managing nodes. | Locks you into AWS. Per-task pricing adds up at scale. |
| **PaaS (Fly.io, Render)** | Product teams that want Heroku ergonomics with container flexibility. | Opinionated platforms. Less control in exchange for faster shipping. |
| **Nomad** | Teams on the HashiCorp stack that want orchestration without the Kubernetes API surface. | Smaller ecosystem. Fewer third-party operators and integrations. |

The common thread is that all three hide more of the operational surface than Kubernetes does, even managed Kubernetes.

## Does managed Kubernetes change the math?

Slightly. Not as much as people assume.

**What EKS, GKE, and AKS remove.** Running etcd. Running the API server, scheduler, and controller manager. HA and patching for the control plane. Real savings, worth having.

**What they do not remove.** The Kubernetes data model. Node pool management. Kubelet. CNI choice. CSI choice. Ingress controller. Upgrade cadence for your node pools. The full operational surface of Deployments, Services, ConfigMaps, RBAC, NetworkPolicies, and the rest. The observability story is unchanged. The need for one engineer with deep cluster expertise is unchanged.

The three-question test still applies to an EKS shop. The break-even point shifts slightly toward adoption, because the control plane is somebody else's problem, but the dominant cost is the mental model and that cost does not go away.

**GKE Autopilot and EKS Fargate-only clusters are a different category.** They hide node management entirely and push you toward a narrower slice of the API. A platform generalist can usually handle these alongside other work. If someone in the discussion is on Autopilot, the "unambiguous owner" rule softens and the break-even point shifts further.

## Three questions before you adopt

The decision framework, stated compactly.

1. **Do you run 15 or more services in production?** If no, a managed container platform will serve you better at a fraction of the operational cost.
2. **Is one engineer the unambiguous owner of the cluster?** If no, pick a platform that hides the cluster entirely. Shared ownership of Kubernetes ends in unowned incidents.
3. **Do you need features only Kubernetes offers, such as custom operators or multi-tenant scheduling?** If no, the ecosystem is not a reason on its own. Reach for it only when the alternatives cannot model your problem.

The threshold is roughly 15 services and one unambiguous cluster owner. Below either, the cost is larger than the benefit.

## The default answer

The default answer to "should we adopt Kubernetes" is no. The burden of proof sits with the team proposing adoption, not with the team proposing an alternative. If the three conditions hold and the three questions resolve cleanly, say yes with confidence. Otherwise, reach for ECS Fargate, Fly.io, or Nomad and revisit the decision when your service count or traffic shape actually changes.

## Notes on the claim softening

An earlier draft used "one engineer owns the cluster full time." That phrasing is accurate for self-managed Kubernetes and overstated for managed Kubernetes. The current copy uses "unambiguous owner" because the failure mode is about clarity of ownership, not hours on the calendar. A 30% time allocation with clear ownership beats a 100% time allocation split across three people.
