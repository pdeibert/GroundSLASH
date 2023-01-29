from typing import Set, Hashable
from dataclasses import dataclass


def scc(nodes: Set[Hashable], edges: Set[Hashable]) -> Set[Hashable]:
    """Implements Tarjan's algorithm for finding strongly connected components.
    
    See Tarjan (1972): "Depth-First Search and Linear Graph Algorithms" for details.
    """

    @dataclass
    class SCCNode:
        """Helper class that wraps original nodes with additional information."""
        node: Hashable
        id: int=-1 # ID of exploration (-1: unexplored)
        low_id: int=-1 # lowest ID of node on stack reachable from this node (including itself; -1: unexplored)
        on_stack: bool=False

    # map original nodes to wrapped counterparts
    node_map = {node: SCCNode(node) for node in nodes}

    # global counter for encountered nodes
    counter = 0
    # stack of explored node that have not been assigned to an SCC yet
    stack = []

    # list of SCCs
    scc_list = []

    def scc_dfs(node: SCCNode):
        # just in case
        nonlocal counter

        # set node id to current global counter
        node.id = counter
        # set lowest reachable id to current global counter (i.e., node itself)
        node.low_id = counter

        # increase global counter
        counter += 1

        # push node to stack (encountered but not yet assigned to an SCC)
        stack.append(node)
        node.on_stack = True

        for (src, dst) in edges:
            # node is not the source of egde
            if src != node.node:
                continue

            # get wrapped target node
            dst = node_map[dst]

            # if target node not visited yet
            if(dst.id == -1):
                # perform DFS from this node
                scc_dfs(dst)
                # update lowest reachable id on stack
                node.low_id = min(node.low_id, dst.low_id)
            # target node visited, but not assigned to an SCC yet (part of current SCC being built)
            elif(dst.on_stack):
                # update lowest reachable id on stack
                node.low_id = min(node.low_id, dst.id)

        # node is root of current SCC being built
        if node.low_id == node.id:

            # initialize new SCC
            scc = []

            root = False

            while not root:
                # pop nodes from stack and add them to SCC until we reach root node
                other = stack.pop()
                other.on_stack = False
                # append original node to SCC
                scc.append(other.node)

                if other == node:
                    root = True

            # store SCC
            scc_list.append(tuple(scc))

    # iterate over nodes
    for node in node_map.values():
        # if node has not been visited yet
        if(node.id == -1):
            # perform DFS from this node
            scc_dfs(node)

    # return SCCs
    return set(scc_list)