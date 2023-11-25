#!/usr/bin/env python3

import typing
from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_internal_representation(nodes_filename, ways_filename):
    """
    Create any internal representation you you want for the specified map, by
    reading the data from the given filenames (using read_osm_data)

    ##Only consider ways with highways

    Once you get all the ways with highways, add only those nodes to a list or a set

    """
    ##Gets a set of valid nodes from the validWays
    waySet = set()

    ##Gets a list of valid ways
    neighbors = {}

    speed={}

    # Goes through the ways in the file
    for way in read_osm_data(ways_filename):
        # Checks for highway tag
        if ('highway' in way['tags']):
            # Checks if the highway is in the allowed highway types
            if (way['tags']['highway'] in ALLOWED_HIGHWAY_TYPES):
                # Adds the node to a set of nodes
                waySet.add(way['nodes'][len(way['nodes'])-1])
                # Goes through the nodes
                for i in range(len(way['nodes']) - 1):
                    # Adds them to waySet
                    waySet.add(way['nodes'][i])
                    # Defines a highwayValue
                    highwayValue = 0

                    # If a maxspeed is given
                    if('maxspeed_mph' in way['tags']):
                        highwayValue = way['tags']['maxspeed_mph']
                    else:
                        highwayValue = DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]

                    # Deals with one way roads
                    if ('oneway' in way['tags'] and way['tags']['oneway'] == 'yes'):
                        # If the node is already in neighbors
                        if (way['nodes'][i] in neighbors):
                            # If a highway value is already in neighbors
                            if((way['nodes'][i + 1]) in neighbors[way['nodes'][i]] ):
                                changeValue = max(highwayValue,neighbors[way['nodes'][i]][(way['nodes'][i + 1])])
                                neighbors[way['nodes'][i]][(way['nodes'][i + 1])] = changeValue
                            # If there is no highway Value associated
                            else:
                                neighbors[way['nodes'][i]][(way['nodes'][i + 1])] = highwayValue
                        # If the node is not in neighbors
                        else:
                            # Creates a dictionary to add to neighbors
                            dict1={}
                            dict1[(way['nodes'][i + 1])] = highwayValue
                            neighbors[way['nodes'][i]] = dict1
                    # Deals with streets that are not one way
                    else:
                        # If the node is in neighbors
                        if (way['nodes'][i] in neighbors):

                            # Checks if the highway value is already in neighbors
                            if(way['nodes'][i + 1] in neighbors[way['nodes'][i]]):
                                changeValue = max(highwayValue, neighbors[way['nodes'][i]][(way['nodes'][i + 1])])
                                neighbors[way['nodes'][i]][(way['nodes'][i + 1])] = changeValue

                            # Otherwise defines highwayValue for the first time
                            else:
                                neighbors[way['nodes'][i]][(way['nodes'][i + 1])] = highwayValue
                        # If the node is not in neighbors
                        else:
                            # Defines a dictionary to be added to neighbros
                            dict1={}
                            dict1[(way['nodes'][i + 1])] = highwayValue
                            neighbors[way['nodes'][i]] = dict1
                        # Checks if the next node is in neighbros
                        if (way['nodes'][i + 1] in neighbors):

                            # Checks if the current node is in the neighbor of the next node and has a highwayValue
                            if((way['nodes'][i]) in neighbors[way['nodes'][i + 1]]):
                                changeValue = max(highwayValue, neighbors[way['nodes'][i + 1]][(way['nodes'][i])])
                                neighbors[way['nodes'][i + 1]][(way['nodes'][i])] = changeValue
                            # Gives it a highway value
                            else:
                                neighbors[way['nodes'][i + 1]][(way['nodes'][i])] = highwayValue
                        # If the node is not in neighbors
                        else:
                            dict2 = {}
                            dict2[(way['nodes'][i])] = highwayValue
                            neighbors[way['nodes'][i + 1]] = dict2

    # Makes a dictionary for the nodes
    nodeSet = {}

    # Goes through the node filename
    for node in read_osm_data(nodes_filename):
        # Adds the node and its information to a set
        if (node['id'] in waySet):
            nodeSet[node['id']] = node

    # Returns the nodeSet, neighbors and the waySet
    return nodeSet, neighbors, waySet


def find_short_path_nodes(map_rep, node1, node2):
    """
    Return the shortest path between the two nodes

    Parameters:
        map_rep: the result of calling build_internal_representation
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2

        Use a uniform cost search
    """
    # Defines the map representation
    nodes, neighbors, third = map_rep

    # Sets agenda to a node, a list of nodes, and a cost
    agenda = [(node1,[node1],0)]

    # Makes an expanded set
    expanded = set()

    # Defines a location 1
    location1 = (nodes[node1]['lat'],nodes[node1]['lon'])

    # Defines a minIndex
    minIndex = 0

    # While agenda is not empty
    while(agenda):
        # Defines a default minCost and minIndex
        minCost = agenda[0][2]
        minIndex = 0

        # Goes through the agenda to find the minCost
        for i in range(len(agenda)):
             if(agenda[i][2] < minCost):
                 minCost = agenda[i][2]
                 # Keeps track of the minimum index
                 minIndex = i

        # Pops the node with the minimum cost
        currentNode, currentList, cost = agenda.pop(minIndex)

        # Gets the first location
        location1 = (nodes[currentNode]['lat'], nodes[currentNode]['lon'])

        # If the currentNode is already in expanded
        if(currentNode in expanded):
            pass
        # If currentNode is the final node
        elif(currentNode==node2):
            print("Length of regular", len(expanded))
            return currentList
        # Otherwise add the node to expanded
        else:
            expanded.add(currentNode)
            # Checks to see if currentNode has neighbors
            if(currentNode in neighbors):
                # Goes through the neighbors of current Node
                for children in neighbors[currentNode]:
                    # If the child is already in expanded
                    if(children in expanded):
                        continue
                    else:
                        # Gets a copy of the list
                        copyList = currentList.copy()
                        # Gets the location of the child
                        location2 = (nodes[children]['lat'],nodes[children]['lon'])
                        # Gets the distance between the current node and the child
                        getDistance = great_circle_distance(location1,location2)

                        # Adds the child to the list
                        copyList.append(children)
                        # Adds the child, the new list, and the new cost to agenda
                        agenda.append((children,copyList,getDistance+cost))

    # Returns None if agenda is empty
    return None

def find_short_path_nodes_heuristics(map_rep, node1, node2):
    """
    Return the shortest path between the two nodes

    Parameters:
        map_rep: the result of calling build_internal_representation
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2

        Use a uniform cost search
    """
    # Defines the map representation
    nodes, neighbors, third = map_rep

    # Sets agenda to a node, a list of nodes, and a cost
    agenda = [(node1,[node1],0,0)]

    # Makes an expanded set
    expanded = set()

    # Defines a location 1
    location1 = (nodes[node1]['lat'],nodes[node1]['lon'])

    # Defines a minIndex
    minIndex = 0

    final_location = (nodes[node2]['lat'], nodes[node2]['lon'])

    # While agenda is not empty
    while(agenda):
        # Defines a default minCost and minIndex
        minCost = agenda[0][2]
        minHeuristic=agenda[0][3]
        minIndex = 0

        # Goes through the agenda to find the minCost
        for i in range(len(agenda)):
             if(agenda[i][3] < minHeuristic):
                 minHeuristic = agenda[i][3]
                 # Keeps track of the minimum index
                 minIndex = i

        # Pops the node with the minimum cost
        currentNode, currentList, cost, heuristic = agenda.pop(minIndex)

        # Gets the first location
        location1 = (nodes[currentNode]['lat'], nodes[currentNode]['lon'])

        # If the currentNode is already in expanded
        if(currentNode in expanded):
            pass
        # If currentNode is the final node
        elif(currentNode==node2):
            print("Length of heuristic", len(expanded))
            return currentList
        # Otherwise add the node to expanded
        else:
            expanded.add(currentNode)
            # Checks to see if currentNode has neighbors
            if(currentNode in neighbors):
                # Goes through the neighbors of current Node
                for children in neighbors[currentNode]:
                    # If the child is already in expanded
                    if(children in expanded):
                        continue
                    else:
                        # Gets a copy of the list
                        copyList = currentList.copy()
                        # Gets the location of the child
                        location2 = (nodes[children]['lat'],nodes[children]['lon'])
                        # Gets the distance between the current node and the child
                        getDistance = great_circle_distance(location1,location2)

                        heuristic_distance = great_circle_distance(location2, final_location)

                        # Adds the child to the list
                        copyList.append(children)
                        # Adds the child, the new list, and the new cost to agenda
                        agenda.append((children,copyList,getDistance+cost, getDistance+cost+heuristic_distance))

    # Returns None if agenda is empty
    return None

def find_short_path(map_rep, loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """

    # Gets the map representation
    nodes,neighbors,waySet=map_rep


    count = 0
    node1 = ''
    # Gets the first node
    for key in nodes:
        if (count == 1):
            break
        node1 = (nodes[key])
        count += 1

    # Sets min distance to a default amount
    minDistance1 = great_circle_distance(loc1, (node1['lat'], node1['lon']))
    minDistance2 = great_circle_distance(loc2, (node1['lat'], node1['lon']))

    # Sets savedNodes to default node
    savedNode1 = node1
    savedNode2 = node1

    # Goes through the nodes to find the closest nodes to the two locations
    for node in nodes:
        if (node in waySet):
            distance1 = (great_circle_distance(loc1, (nodes[node]['lat'], nodes[node]['lon'])))
            if (distance1 < minDistance1):
                minDistance1 = distance1
                savedNode1 = nodes[node]

            distance2=(great_circle_distance(loc2, (nodes[node]['lat'], nodes[node]['lon'])))
            if (distance2 < minDistance2):
                minDistance2 = distance2
                savedNode2 = nodes[node]


    # Gets a list of nodes calling the previous function
    listNodes=find_short_path_nodes(map_rep,savedNode1['id'],savedNode2['id'])

    # If listNodes is empty
    if listNodes is None:
        return None
    listLocations=[]

    # Converts each node to a latitude and longitude
    for node in listNodes:
        listLocations.append((nodes[node]['lat'],nodes[node]['lon']))

    return listLocations

def find_short_path_heuristics(map_rep, loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """

    # Gets the map representation
    nodes,neighbors,waySet=map_rep


    count = 0
    node1 = ''
    # Gets the first node
    for key in nodes:
        if (count == 1):
            break
        node1 = (nodes[key])
        count += 1

    # Sets min distance to a default amount
    minDistance1 = great_circle_distance(loc1, (node1['lat'], node1['lon']))
    minDistance2 = great_circle_distance(loc2, (node1['lat'], node1['lon']))

    # Sets savedNodes to default node
    savedNode1 = node1
    savedNode2 = node1

    # Goes through the nodes to find the closest nodes to the two locations
    for node in nodes:
        if (node in waySet):
            distance1 = (great_circle_distance(loc1, (nodes[node]['lat'], nodes[node]['lon'])))
            if (distance1 < minDistance1):
                minDistance1 = distance1
                savedNode1 = nodes[node]

            distance2=(great_circle_distance(loc2, (nodes[node]['lat'], nodes[node]['lon'])))
            if (distance2 < minDistance2):
                minDistance2 = distance2
                savedNode2 = nodes[node]


    # Gets a list of nodes calling the previous function
    listNodes=find_short_path_nodes_heuristics(map_rep,savedNode1['id'],savedNode2['id'])

    # If listNodes is empty
    if listNodes is None:
        return None
    listLocations=[]

    # Converts each node to a latitude and longitude
    for node in listNodes:
        listLocations.append((nodes[node]['lat'],nodes[node]['lon']))

    return listLocations

def find_fast_path(map_rep, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """

    # Defines the map representation
    nodes, neighbors, waySet = map_rep

    count = 0
    nodeA = ''
    # Defines a default node
    for key in nodes:
        if (count == 1):
            break
        nodeA = (nodes[key])
        count += 1

    # Defines default distances
    minDistance1 = great_circle_distance(loc1, (nodeA['lat'], nodeA['lon']))
    minDistance2 = great_circle_distance(loc2, (nodeA['lat'], nodeA['lon']))

    # Defines savedNode1 and 2
    savedNode1 = nodeA
    savedNode2 = nodeA

    # Finds the closest nodes to savedNode1 and savedNode2
    for node in nodes:
        if (node in waySet):
            distance1 = (great_circle_distance(loc1, (nodes[node]['lat'], nodes[node]['lon'])))
            if (distance1 < minDistance1):
                minDistance1 = distance1
                savedNode1 = nodes[node]

            distance2 = (great_circle_distance(loc2, (nodes[node]['lat'], nodes[node]['lon'])))
            if (distance2 < minDistance2):
                minDistance2 = distance2
                savedNode2 = nodes[node]

    # print("SAVED NODE 1",savedNode1, 'AYO')

    # Redefines node1 and node2
    node1 = savedNode1['id']
    node2 = savedNode2['id']

    # Keeps track of a node, a list of nodes and a cost
    agenda = [(node1, [node1], 0)]

    # Defines an expanded set
    expanded = set()

    # Defines a location for the first node
    location1 = (nodes[node1]['lat'], nodes[node1]['lon'])

    minIndex = 0

    # While agneda is not empty
    while (agenda):
        # Defines a default minCost and minIndex
        minCost = agenda[0][2]
        minIndex = 0

        # Goes through the agenda to find a minCost
        for i in range(len(agenda)):
            if (agenda[i][2] < minCost):
                minCost = agenda[i][2]
                minIndex = i

        # Gets the information of the minIndex node
        currentNode, currentList, cost = agenda.pop(minIndex)
        # Gets the location of the currentNode
        location1 = (nodes[currentNode]['lat'], nodes[currentNode]['lon'])
        # If the currentNode is in expanded
        if (currentNode in expanded):
            pass
        # If the node is the final Node
        elif (currentNode == node2):
            listNodes = currentList

            if listNodes is None:
                return None
            listLocations = []

            # Gets the lat and lon the nodes
            for node in listNodes:
                listLocations.append((nodes[node]['lat'], nodes[node]['lon']))

            # Returns the list of locations
            return listLocations

        # Otherwise add the currentNode to an expanded set
        else:
            expanded.add(currentNode)
            # If the currentNode has children
            if (currentNode in neighbors):
                # Goes through the children of currentNode
                for children in neighbors[currentNode]:
                    # If the child is in expanded
                    if (children in expanded):
                        continue
                    else:
                        # Gets a copy of the list
                        copyList = currentList.copy()
                        # Gets the location of the child
                        location2 = (nodes[children]['lat'], nodes[children]['lon'])
                        # Finds the distance between the currentNode and the child
                        getDistance = great_circle_distance(location1, location2)
                        # Gets the speed of the child
                        speed = neighbors[currentNode][children]

                        # Finds the time to get to the distance with the speed
                        time = getDistance/speed

                        # Adds the child to a list
                        copyList.append(children)

                        # Appends the information to the agenda
                        agenda.append((children, copyList, time + cost))

    return None


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.

    count=0

    for way in read_osm_data('resources/mit.ways'):
        print(way)

    #print("CHECK")
    x,y,z=(build_internal_representation('resources/mit.nodes', 'resources/mit.ways'))
    print(x)
    print()
    print(y)
    print()
    print(z)

    print()


    loc1 = (42.3575, -71.0956)  # Parking Lot - end of a oneway and not on any other way
    loc2 = (42.3575, -71.0940)  # close to Kresge

    nodeID=2
    ##Come Back
    totalDict={}
    dict1={}
    dict1[1]=45
    totalDict[nodeID]= {}
    print(totalDict)
    totalDict[nodeID][1] = 45
    print(totalDict)
    totalDict[nodeID][8] = 10
    print(totalDict)
    #totalDict[nodeID][4]=

    for keys in totalDict[nodeID]:
        print(keys)

    print(find_short_path_nodes_heuristics((x,y,z),2,8))


    a,b,c = build_internal_representation('resources/cambridge.nodes','resources/cambridge.ways')

    location1= (42.3858, -71.0783)
    location2= (42.5465, -71.1787)

    find_short_path((a,b,c),location1,location2)
    find_short_path_heuristics((a,b,c),location1,location2)
