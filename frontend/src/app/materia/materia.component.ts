import { Component, Input } from '@angular/core';
import { Materia } from '../materia';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-materia',
  imports: [CommonModule],
  templateUrl: './materia.component.html',
  styleUrl: './materia.component.scss'
})

export class MateriaComponent {
  @Input() mat!:Materia;
}
