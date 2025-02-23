import { Component, signal } from '@angular/core';
import exampleGraph from './assets/example-graph.json';
import { NavBarComponent } from "./views/nav-bar/nav-bar.component";
import { ThreeDComponent } from "./views/three-d/three-d.component";
import { UsageComponent } from "./views/usage/usage.component";

@Component({
  selector: 'app-root',
  imports: [UsageComponent, ThreeDComponent, NavBarComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {

  protected graphFile = signal<string>(exampleGraph.gexfFile);
  protected show_usage = signal<boolean>(false);

  protected onNavClick(path: string) {
    if (path === '/usage') {
      this.show_usage.set(true);
    } else {
      this.show_usage.set(false);
    }
  }

  protected onFileInput(graphFile: string) {
    this.graphFile.set(graphFile);
  }
}
