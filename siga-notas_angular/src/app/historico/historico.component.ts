import { Component } from '@angular/core';
import { MateriaComponent } from '../materia/materia.component';
import { RouterLink } from '@angular/router';
import { NgIf, CommonModule } from '@angular/common';
import { MateriaService } from '../materia.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-historico',
  imports: [MateriaComponent, RouterLink, NgIf, CommonModule],
  templateUrl: './historico.component.html',
  styleUrl: './historico.component.scss'
})
export class HistoricoComponent {
  constructor(protected materiaService: MateriaService) {}
  
  visualizacao = false;
  
  ngOnInit(): void {
    setTimeout(() => {
      this.visualizacao = true;
    }, 100);
  } // ngOnInit()
}
