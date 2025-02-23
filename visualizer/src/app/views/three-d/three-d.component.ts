import { Component, input } from '@angular/core';
import { Graph3d } from '../../graph/graph';

@Component({
  selector: 'msg-three-d',
  imports: [],
  templateUrl: './three-d.component.html',
  styleUrl: './three-d.component.scss',
})
export class ThreeDComponent {
  public graphFile = input.required<string>();

  private graph: Graph3d | null = null;

  ngOnInit() {
    this.graph = new Graph3d(this.graphFile());
    this.graph.bindTo(document.getElementById('graph-3d')!);
  }

  ngOnChanges() {
    this.graph = new Graph3d(this.graphFile());
    this.graph.bindTo(document.getElementById('graph-3d')!);
  }

  protected onMouseEnter() {
    if (!this.graph) {
      return;
    }
    this.graph.start();
  }

  protected onMouseLeave() {
    if (!this.graph) {
      return;
    }
    this.graph.pause();
  }
}
