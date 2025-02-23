
export interface Coords {
  x: number;
  y: number;
  z: number;
}

export interface JsonGraph {
  gexf: {
    graph: {
      nodes: {
        node: {
          id: string;
          label: string;
        }[];
      };
      edges: {
        edge: {
          source: string;
          target: string;
        }[];
      };
    };
  };
}

export interface Node {
  id: string;
  name: string;
  community: number;
  neighbors: string[];
  links: string[];
  color: string;
  __bckgDimensions?: number[];
}

export interface Link {
  source: string;
  target: string;
  id: string;
  community: number;
}
