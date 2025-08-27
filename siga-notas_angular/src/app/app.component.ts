import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  // template: `
    
  // `,
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'siga-notas';
}
