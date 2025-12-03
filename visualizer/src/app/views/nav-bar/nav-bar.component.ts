import { Component, output, signal } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'msg-nav-bar',
  imports: [RouterModule],
  templateUrl: './nav-bar.component.html',
  styleUrl: './nav-bar.component.scss',
})
export class NavBarComponent {
  protected onNavClick = output<string>();
  protected onFileInput = output<string>();
  protected filename = signal<string>('');

  protected handleFileInput(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input && input.files) {
      const files = input.files;
      const file = files.item(0)!;
      this.filename.set(file.name);
      const fileReader = new FileReader();

      fileReader.readAsText(file, 'UTF-8');
      fileReader.onload = () => {
        const file = fileReader.result as string;
        this.onFileInput.emit(file);
      };
    }
  }
}
