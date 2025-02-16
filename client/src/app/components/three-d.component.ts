import ForceGraph3D from '3d-force-graph';
import { Component, OnInit } from '@angular/core';
import { NodeObject } from 'three-forcegraph';
import SpriteText from 'three-spritetext';
import jLouvain from './jLouvain';


@Component({
  selector: 'msg-three-d',
  imports: [],
  templateUrl: './three-d.component.html',
  styleUrl: './three-d.component.scss',
})
export class ThreeDComponent implements OnInit {
  // export default function App() {
  //   const containerRef = useRef(null);
  //   useEffect(() => {
  //     const Graph = ForceGraph3D({ controlType: "orbit" })(containerRef.current)
  //       .graphData(data)

  private lightenDarkenColor(css_color: string, amount: number): string {
    const color = parseInt(css_color.slice(1), 16);
    const r = Math.min(255, Math.max(0, ((color >> 16) & 0xFF) + amount));
    const b = Math.min(255, Math.max(0, ((color >> 8) & 0xFF) + amount));
    const g = Math.min(255, Math.max(0, (color & 0x0000FF) + amount));
    return '#' + (
      g | (b << 8) | (r << 16)
    ).toString(16).padStart(6, '0');
  }

  ngOnInit(): void {}

  private parseXml(xml: string, arrayTags: string | any[]) {
    let dom = null;
    if (window.DOMParser)
      dom = new DOMParser().parseFromString(xml, 'text/xml');
    else if (window.ActiveXObject) {
      dom = new ActiveXObject('Microsoft.XMLDOM');
      dom.async = false;
      if (!dom.loadXML(xml))
        throw dom.parseError.reason + ' ' + dom.parseError.srcText;
    } else throw new Error('cannot parse xml string!');

    function parseNode(
      xmlNode: {
        nodeName: string;
        nodeValue: any;
        attributes: any;
        childNodes: any;
      },
      result: { [x: string]: {} }
    ) {
      if (xmlNode.nodeName == '#text') {
        let v = xmlNode.nodeValue;
        if (v.trim()) result['#text'] = v;
        return;
      }

      let jsonNode: { [key: string]: any } = {},
        existing = result[xmlNode.nodeName];
      if (existing) {
        if (!Array.isArray(existing))
          result[xmlNode.nodeName] = [existing, jsonNode];
        else (result[xmlNode.nodeName] as any[]).push(jsonNode);
      } else {
        if (arrayTags && arrayTags.indexOf(xmlNode.nodeName) != -1)
          result[xmlNode.nodeName] = [jsonNode];
        else result[xmlNode.nodeName] = jsonNode;
      }

      if (xmlNode.attributes)
        for (let attribute of xmlNode.attributes)
          jsonNode[attribute.nodeName] = attribute.nodeValue;

      for (let node of xmlNode.childNodes) parseNode(node, jsonNode);
    }

    let result = {};
    for (let node of dom.childNodes) parseNode(node, result);

    return result;
  }

  protected handleFileInput(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input && input.files) {
      const files = input.files;
      const file = files.item(0)!;
      const fileReader = new FileReader();
      fileReader.readAsText(file, 'UTF-8');
      fileReader.onload = () => {

        const graph = this.parseXml(fileReader.result as string, []);

        const ele = document.getElementById('graph-3d');

        interface Gexf {
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

        interface CustomNode {
          id: string;
          name: string;
          community: number;
          neighbors: string[];
          links: string[];
          color: string;
        }

        interface CustomLink {
          source: string;
          target: string;
          id: string;
          community: number;
        }

        interface MyGraph {
          nodes: CustomNode[];
          links: CustomLink[];
        }

        const data: MyGraph = {
          nodes: (graph as Gexf).gexf.graph.nodes.node.map((node) => ({
            id: node.id,
            name: node.label,
            community: 1,
            neighbors: [],
            links: [],
            color: ''
          })),
          links: (graph as Gexf).gexf.graph.edges.edge.map((edge, i) => ({
            source: edge.source,
            target: edge.target,
            id: i.toString(),
            community: 1
          })),
        };

        data.links.forEach((link) => {
          const a = data.nodes.find((node) => node.id === link.source)!;
          const b = data.nodes.find((node) => node.id === link.target)!;
          a.neighbors.push(b.id);
          b.neighbors.push(a.id);

          a.links.push(link.id);
          b.links.push(link.id);
        });

        const nodes = data.nodes.map((node) => node.id);
        const edges = data.links.map((link) => ({
          source: link.source,
          target: link.target,
          weight: 1
        }));


        let result = jLouvain().nodes(nodes).edges(edges)();

        data.nodes.map((node) => {
          node.community = result[node.id];
          return node;
        });

        data.links.map((link) => {
          link.community = result[link.source];
          return link;
        });

        const highlightNodes = new Set();
        const highlightLinks = new Set();
        let hoverNode: NodeObject | null = null;

        const myGraph = new ForceGraph3D(ele!, { controlType: 'orbit' })
          .graphData(data)
          .numDimensions(3)
          // .backgroundColor("#000")
          // .showNavInfo(false)

          .nodeAutoColorBy('community')
          .onNodeDragEnd((node) => {
            node.fx = node.x;
            node.fy = node.y;
            node.fz = node.z;
          })
          .nodeThreeObject((node) => {
            const sprite = new SpriteText((node as CustomNode).name);
            sprite.backgroundColor = 'rgba(0, 0, 0, 0)';
            sprite.color = (node as CustomNode).color;
            sprite.textHeight = 8 + ((node as CustomNode).neighbors.length / data.nodes.length)*64;
            sprite.material.depthWrite = false;
            sprite.strokeColor = 'rgba(0, 0, 0, 0)';

            if (highlightNodes.has((node as CustomNode).id)) {
              sprite.color = this.lightenDarkenColor((node as CustomNode).color, 100);
            }

            return sprite;

            // ContainerText.backgroundColor = 'rgba(0,0,190,0)';
            // const canvas = document.createElement('canvas');
            // const context = canvas.getContext('2d')!;
            // canvas.width = 512;
            // canvas.height = 256;
            // context.font = '24px Arial';
            // context.fillStyle = 'rgba(255, 255, 255, 1.0)';
            // context.textAlign = 'left';
            // context.textBaseline = 'middle';
            // context.fillText((node as CustomNode).name, canvas.width / 2, canvas.height / 2);
            // const texture = new Texture(canvas);
            // texture.needsUpdate = true;
            // const spriteMaterial = new SpriteMaterial({ map: texture, depthWrite: false });
            // const sprite = new Sprite(spriteMaterial);
            // sprite.scale.set(75, 75, 1);
          })

          .linkAutoColorBy('community')
          .linkWidth((link) => highlightLinks.has((link as CustomLink).id) ? 4 : 0.5)
          .linkOpacity(0.2)
          .linkDirectionalParticles((link) => highlightLinks.has((link as CustomLink).id) ? 4 : 0)
          .linkDirectionalParticleWidth(4)

          .cooldownTime(15000)
          .enableNodeDrag(false)

          .onNodeHover((arg) => {

            const node = arg as CustomNode;
            // no state change
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

            // trigger update of highlighted objects in scene
            myGraph
              .nodeThreeObject(myGraph.nodeThreeObject())
              .linkWidth(myGraph.linkWidth())
              .linkDirectionalParticles(myGraph.linkDirectionalParticles());
          })
          .onNodeClick((node) => {
            // Aim at node from outside it
            const distance = 40;
            const distRatio = 1 + distance / Math.hypot(node.x || 0, node.y || 0, node.z || 0);

            myGraph.cameraPosition(
              {
                x: (node.x || 0) * distRatio,
                y: (node.y || 0) * distRatio,
                z: (node.z || 0) * distRatio
              },
              { x: node.x || 0, y: node.y || 0, z: node.z || 0 },
              3000
            );
          });

        // setInterval(() => {
        //     const { nodes, links } = myGraph.graphData();
        //     const id = nodes.length;
        //     console.log('id:', id);
        //     console.log(data.links.filter(link => link.source <= id+1 && link.target <= id+1));
        //     myGraph.graphData({
        //         // get first id + 1 from data
        //         nodes: data.nodes.slice(0, id + 1),
        //         links: data.links.filter(link => link.source <= id+1 && link.target <= id+1)
        //     });
        // }, 1000);

        // Spread nodes a little wider
        myGraph.d3Force('charge')!['strength'](-800);
      };
    }
  }
}
