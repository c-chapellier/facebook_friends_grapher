import { Component, signal } from '@angular/core';
import exampleGraph from './assets/example-graph.json';
import { NavBarComponent } from './views/nav-bar/nav-bar.component';
import { ThreeDComponent } from './views/three-d/three-d.component';

@Component({
  selector: 'app-root',
  imports: [ThreeDComponent, NavBarComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  protected graphFile = signal<string>(exampleGraph.gexfFile);

  protected onFileInput(graphFile: string) {
    this.graphFile.set(graphFile);
  }
}
