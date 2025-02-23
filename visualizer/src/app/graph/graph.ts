import ForceGraph3D, { ForceGraph3DInstance } from '3d-force-graph';
import { color as d3Color, RGBColor } from 'd3';
import { LinkObject, NodeObject } from 'three-forcegraph';
import SpriteText from 'three-spritetext';
import * as THREE from '../../../node_modules/@types/three';
import { hexColors, lightenDarkenColor } from './colors';
import communityDetectionLouvain from './community-detection-Louvain';
import { Coords, JsonGraph, Link, Node } from './types';
import { parseXml } from './xml-parser';

interface Graph3dOptions {
  nodeHighlighting?: boolean;
  gradientLinks?: boolean;
  linksOpacity?: number;
}

export class Graph3d {
  private forceGraph: ForceGraph3DInstance<NodeObject, LinkObject<NodeObject>> | null = null;
  private ticks = 0;
  private isStatic = false;
  private options: Graph3dOptions = {
    nodeHighlighting: true,
    gradientLinks: true,
    linksOpacity: 0.2,
  };

  public nodes: Node[] = [];
  public links: Link[] = [];

  constructor(gexfFile: string, options?: Graph3dOptions) {
    this.options = { ...this.options, ...options };

    const jsonGraph = parseXml(gexfFile, []) as JsonGraph;

    this.nodes = jsonGraph.gexf.graph.nodes.node.map((node) => ({
      id: node.id,
      name: node.label,
      community: 1,
      neighbors: [],
      links: [],
      color: '',
    }));
    this.links = jsonGraph.gexf.graph.edges.edge.map((edge, i) => ({
      source: edge.source,
      target: edge.target,
      id: i.toString(),
      community: 1,
    }));

    this.links.forEach((link) => {
      const a = this.nodes.find((node) => node.id === link.source)!;
      const b = this.nodes.find((node) => node.id === link.target)!;
      a.neighbors.push(b.id);
      b.neighbors.push(a.id);
      a.links.push(link.id);
      b.links.push(link.id);
    });

    this.add_communites();
  }

  private add_communites() {
    const result = communityDetectionLouvain()
      .nodes(this.nodes.map((node) => node.id))
      .edges(
        this.links.map((link) => ({
          source: link.source,
          target: link.target,
          weight: 1,
        }))
      )();

    this.nodes.map((node) => {
      node.community = result[node.id];
      return node;
    });

    this.links.map((link) => {
      link.community = result[link.source];
      return link;
    });

    console.log('number of communities:', new Set(this.nodes.map((node) => node.community)).size);
  }

  public bindTo(element: HTMLElement) {
    const highlightNodes = new Set();
    const highlightLinks = new Set();
    let hoverNode: NodeObject | null = null;

    this.forceGraph = new ForceGraph3D(element, { controlType: 'orbit' })
      .graphData(this)
      .numDimensions(3)
      .backgroundColor('#1e1e1e')
      .width(element.clientWidth)
      .height(element.clientHeight)
      .onNodeDragEnd((node) => {
        node.fx = node.x;
        node.fy = node.y;
        node.fz = node.z;
      })
      .nodeThreeObject((node) => {
        const sprite = new SpriteText((node as Node).name);
        sprite.textHeight = 8 + ((node as Node).neighbors.length / this.nodes.length) * 64;
        sprite.material.depthWrite = false;

        (node as Node).color = hexColors[(node as Node).community % hexColors.length];
        sprite.color = (node as Node).color;

        if (this.options.nodeHighlighting) {
          // if (highlightNodes.size !== 0) {
          //   sprite.color = lightenDarkenColor((node as Node).color, +50);
          // }
          if (highlightNodes.has((node as Node).id)) {
            console.log('ok');
            sprite.backgroundColor = lightenDarkenColor((node as Node).color, -50);
            sprite.material.depthWrite = true;
            // sprite.color = lightenDarkenColor((node as Node).color, 100);
          }
        }

        return sprite;
      })
      .cooldownTime(45000)
      .enableNodeDrag(false)
      .onEngineTick(() => {
        if (this.isStatic) {
          return;
        }
        if (this.ticks === 0) {
          if (this.options.gradientLinks) {
            this.forceGraph!
              .linkThreeObject(link => {
                const colors = new Float32Array([
                  this.nodes.find((node) => node.id === (link.source as NodeObject).id)!.color,
                  this.nodes.find((node) => node.id === (link.target as NodeObject).id)!.color
                ]
                  .map(node => d3Color(node as string))
                  .map((color) => {
                    if (color) {
                      const { r, g, b } = color as RGBColor;
                      return [r, g, b].map(v => v / 255);
                    }
                    return [0, 0, 0];
                  }).flat()
                );

                const geometry = new THREE.BufferGeometry();
                geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(2 * 3), 3));
                geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

                return new THREE.Line(
                  geometry,
                  new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: this.options.linksOpacity! })
                );
              })
              .linkPositionUpdate((line, { start, end }: { start: Coords; end: Coords; }) => {
                const startR = this.forceGraph!.nodeRelSize();
                const endR = this.forceGraph!.nodeRelSize();
                const lineLen = Math.sqrt((['x', 'y', 'z'] as (keyof Coords)[]).map(
                  (dim) => Math.pow(
                    (end[dim] || 0) - (start[dim] || 0), 2)
                  ).reduce((acc, v) => acc + v, 0)
                );

                const linePos = (line as THREE.Line).geometry.getAttribute('position');

                // calculate coordinate on the node's surface instead of center
                const positions = [startR / lineLen, 1 - endR / lineLen]
                  .map(t => (
                    ['x', 'y', 'z'] as Array<keyof Coords>).map((dim) =>
                      start[dim] + (end[dim] - start[dim]) * t
                    )
                  ).flat();

                for (let i = 0; i < positions.length; i += 3) {
                  linePos.setXYZ(i / 3, positions[i], positions[i + 1], positions[i + 2]);
                }
                linePos.needsUpdate = true;
                return true;
              });
          } else {
            this.forceGraph!
              .linkColor((link) => (link.source! as Node).color)
              .linkWidth((link) => (highlightLinks.has((link as Link).id) ? 4 : 0.5))
              .linkOpacity(this.options.linksOpacity!)
              .linkDirectionalParticles((link) =>
                highlightLinks.has((link as Link).id) ? 4 : 0
              );
          }
        }
        ++this.ticks;
        if (this.ticks % 4 === 0) {
          this.forceGraph!.zoomToFit(0, -500);
          this.isStatic = this.forceGraph!.graphData().nodes.every(
            (node: NodeObject) => {
              // console.log('vx:', node.vx, 'vy:', node.vy, 'vz:', node.vz);
              return (Math.abs(node.vx!) < 4 && Math.abs(node.vy!) < 4 && Math.abs(node.vz!) < 4);
            }
          );
          if (this.isStatic) {
            console.log('Static layout reached');
            if (this.options.nodeHighlighting) {
              this.forceGraph!.onNodeHover((arg: any) => {

                console.log('hover:', arg);
                const node = arg as Node;
                if ((!node && !highlightNodes.size) || (node && hoverNode === node))
                  return;

                highlightNodes.clear();
                highlightLinks.clear();
                if (node) {
                  highlightNodes.add(node);
                  node.neighbors.forEach((neighbor) => highlightNodes.add(neighbor));
                  node.links.forEach((link) => highlightLinks.add(link));
                }
                hoverNode = node || null;

                this.forceGraph!
                  .nodeThreeObject(this.forceGraph!.nodeThreeObject())
                  .linkWidth(this.forceGraph!.linkWidth())
                  .linkDirectionalParticles(this.forceGraph!.linkDirectionalParticles());
              });
            }
          }
        }
      });

      if (this.options.nodeHighlighting) {
        this.forceGraph.linkDirectionalParticleWidth(4)
      }

      // setInterval(() => {
    //     const { nodes, links } = graph.graphData();
    //     const id = nodes.length;
    //     console.log('id:', id);
    //     console.log(data.links.filter(link => link.source <= id+1 && link.target <= id+1));
    //     graph.graphData({
    //         // get first id + 1 from data
    //         nodes: data.nodes.slice(0, id + 1),
    //         links: data.links.filter(link => link.source <= id+1 && link.target <= id+1)
    //     });
    // }, 1000);

    // Spread nodes a little wider
    // 500 nodes: -800
    this.forceGraph.d3Force('charge')!['strength'](-1200);
    this.pause();
  }

  public start() {
    this.resume();
  }

  public pause() {
    if (!this.forceGraph) {
      return ;
    }
    this.forceGraph.pauseAnimation();
  }

  public resume() {
    if (!this.forceGraph) {
      return ;
    }
    this.forceGraph.resumeAnimation();
  }
}
