import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HomeComponent } from "./components/home.component";
import { ThreeDComponent } from "./components/three-d.component";
import { UsageComponent } from "./components/usage.component";

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, HomeComponent, UsageComponent, ThreeDComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {

}
