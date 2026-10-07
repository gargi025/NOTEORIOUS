import matplotlib.pyplot as plt
import networkx as nx


def draw_knowledge_graph(graph):

    if len(graph.nodes) == 0:
        return None

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    positions = nx.spring_layout(
        graph,
        seed=42,
        k=1.5
    )

    nx.draw_networkx_nodes(
        graph,
        positions,
        ax=ax,
        node_size=2500
    )

    nx.draw_networkx_edges(
        graph,
        positions,
        ax=ax,
        arrows=True,
        arrowsize=20,
        width=2
    )

    nx.draw_networkx_labels(
        graph,
        positions,
        ax=ax,
        font_size=10
    )

    edge_labels = nx.get_edge_attributes(
        graph,
        "relation"
    )

    nx.draw_networkx_edge_labels(
        graph,
        positions,
        edge_labels=edge_labels,
        ax=ax,
        font_size=9
    )

    ax.axis("off")

    return fig