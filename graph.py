from __future__ import annotations
from numpy import infty, zeros
from math import *
import graphviz as gv
from typing import Any

class Graph:

  #Inicializa las listas de vértices y aristas.
  def __init__( self ):
    self._vertices: list[Graph.Vertex] = []
    self._edges: list[Graph.Edge] = []
    self.identifier = 'Code' #Define un identificador predeterminado para los vértices.

  # Devuelve una representación en cadena del grafo.
  def __repr__( self ): return f"Graph: ( \n \t Vertices: { self._vertices }, \n \t Edges: { self._edges } \n)"

  @property
  #Devuelve una copia de la lista de vértices
  def vertices( self ) -> list[Graph.Vertex] : return self._vertices.copy()

  @property
  #Devuelve una lista de diccionarios que representan los datos de los vértices.
  def data(self) -> list[dict] : return [ v.data for v in self._vertices ]

  @property
  #Devuelve una copia de la lista de aristas.
  def edges( self ) -> list[Graph.Edge] : return self._edges.copy()

  @property
  #Calcula y devuelve una matriz de costos entre los vértices.
  def costMatrix( self ) -> list[list[int]]:
    vertexNumber = len(self._vertices)
    matrix = [ [ 0 for i in range( vertexNumber ) ] for j in range( vertexNumber ) ]
    for edge in self.edges:
      i, j = self.vertices.index( edge.vertices[0] ), self._vertices.index( edge.vertices[1] )
      matrix[i][j] = matrix[j][i] = edge.weight
    return matrix

  class Vertex:
    #Inicializa los datos del vértice, su identificador y una lista de aristas conectadas a él.
    def __init__( self, data ):
      self.data: dict = data
      self.identifier = 'Code'
      self.edges: list[Graph.Edge] = []

    def __repr__( self ):
      return str( self.data[self.identifier] )

    #Implementa la comparación de menor que para vértices.
    def __lt__( self, vertex ): # <
      for i in vertex.edges:
        if i.vertices[1] == self: return True
      return False

    def __gt__( self, vertex ): # >
      for i in self.edges:
        if i.vertices[1] == vertex: return True
      return False

    def __le__( self, vertex ): # <=
      return self < vertex

    def __ge__( self, vertex ): # =>
      return self > vertex

    def __eq__( self, compare ):
      if isinstance( compare, Graph.Vertex ) : return self.data == compare.data
      elif isinstance( compare, dict )       : return self.data == compare
      elif isinstance( compare, int )        : return self.data[ self.identifier ] == compare
      return False

    def __hash__(self):
      return hash(str(self.data[self.identifier]))

  class Edge:

    #Inicializa los vértices de origen y destino y el peso de la arista.
    def __init__( self, fromVertex: Graph.Vertex, toVertex: Graph.Vertex, weight ):
      self.vertices: tuple(Graph.Vertex,Graph.Vertex) = ( fromVertex, toVertex ) # type: ignore
      self.weight = weight

    def __repr__( self ):
      return f"( {self.weight}:{self.vertices[0]} <-> {self.vertices[1]} )"

  #Agrega un nuevo vértice al grafo.
  def newVertex( self, data ):
    self._vertices.append( self.Vertex( data ) )

  #Agrega una nueva arista entre dos vértices con un peso dado.
  def newEdge( self, source: str, destination: str, weight: float ):

    source = self.getVertex(source)
    destination = self.getVertex(destination)

    edge = self.Edge( source, destination, weight )

    source.edges.append( edge )
    destination.edges.append( self.Edge( destination, source, weight ) )

    self._edges.append( edge )

  #Obteniene un vértice específico según su valor.
  def getVertex( self, value ):
    left = 0 #índice izquierdo al comienzo de la lista de vértices.
    right = len( self.vertices ) - 1 #índice derecho al final de la lista de vértices.

    #Búsqueda binaria para encontrar el vértice
    while left <= right:
        mid = left + (right - left) // 2 #índice medio del rango actual.
        vertex = self.vertices[mid].data[self.identifier]
        if vertex == value: return self.vertices[mid]
        elif vertex < value: left = mid + 1
        else: right = mid - 1
    return None

  def addVertex( self, vertex ):
    self._vertices.append( vertex )


  #Calcula la distancia entre dos vértices en coordenadas geográficas.
  def distance( self, source, destination ):

    source = self.getVertex( source )
    destination = self.getVertex( destination )

    # Radio medio de la Tierra en kilómetros
    earth_radius = 6371

    # Convierte las coordenadas de grados a radianes
    lt0 = radians(source.data['Latitude'])
    ln0 = radians(source.data['Longitude'])
    ltf = radians(destination.data['Latitude'])
    lnf = radians(destination.data['Longitude'])

    # Diferencia de latitud y longitud.
    dlt = ltf - lt0
    dln = lnf - ln0

    # Fórmula de Haversine.
    a = sin( dlt / 2 )**2 + cos(lt0) * cos(ltf) * sin(dln / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius * c # Distancia en kilómetros.


  #Obtiene una lista de rutas en el grafo.
  def getRoutes( self ):
    routes = []
    for e in self.edges:
      s = e.vertices[0].data
      d = e.vertices[1].data
      route = {
          'Source': ( s['Latitude'], s['Longitude'] ),
          'Destination': ( d['Latitude'], d['Longitude'] ),
          'Weight': e.weight
          }
      routes.append(route)
    return routes

  #Algoritmo de Dijkstra para encontrar los caminos más corto desde un vértice de inicio.
  def dijkstra( self, start ):

    paths = { v: ( infty, None ) for v in self.vertices } #Diccionario para mantener las distancias más cortas y los predecesores.
    paths[start] = ( 0, None ) #Distancia desde el vértice de inicio a sí mismo como 0 y sin predecesor.

    toVisit = self.vertices #Lista con todos los vértices para visitar.
    if start in toVisit: toVisit.remove( start ) #Elimina el vértice de inicio de la lista de vértices a visitar.

    for e in start.edges:
      paths[ e.vertices[1] ] = ( e.weight, start )

    while toVisit:
      toVisit = sorted( toVisit, key = lambda x: paths[x] ) #Ordena la lista según distancias actuales.
      min = toVisit.pop(0) #Vértice con la distancia más corta del vértice de inicio.

      #Recorre las aristas saliende de min.
      for e in min.edges:
        if paths[min][0] + e.weight < paths[ e.vertices[1] ][0]:
          paths[ e.vertices[1] ] = ( paths[min][0] + e.weight, min ) #Actualiza la distancia y el predecesor

    return(paths)

  #Determina el camino mínimo entre dos vértices.
  def getPath( self, minpaths, source, destination ):

    #Comprueba si el destino no está en 'minpaths' o si su distancia es infinita.
    if not destination in minpaths or minpaths[destination] == ( infty, None ):
      return f"{source} -/-> {destination} "

    weight = minpaths[destination][0] #Peso del camino más corto desde el inicio hasta el destino.
    path = f"{destination}" #Inicializa una cadena 'path' con el vértice de destino.

    #Mientras el vértice actual no sea igual al vértice de inicio.
    while not source == destination:
      destination = minpaths[destination][1] #Obtiene el predecesor del vértice actual.
      path = f"{destination} -> " + path #Agrega el vértice actual al camino.

    #Construye y devuelve una cadena que representa el camino más corto.
    return f"({round(weight,3)}): " + path

  #Visualización del mapa.
  def display( self ):
    plot = gv.Graph( comment = "Graph", engine = 'sfdp' )
    for vertex in self.vertices:
      plot.node( str(vertex) )
    for edge in self.edges:
      plot.edge( str(edge.vertices[0]), str(edge.vertices[1]), label = str(round(edge.weight,3)) )
    return plot