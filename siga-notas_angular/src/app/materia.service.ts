import { Injectable } from '@angular/core';
import { Materia } from './materia';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MateriaService {
  protected parciais: Materia [] = []
  protected historicas: Materia[] = [];
  private atualizarNotasSubject = new Subject<void>();
  private notasCarregando = true;
  atualizarNotas$ = this.atualizarNotasSubject.asObservable();


  constructor() { }

  emitirAtualizacao(): void {
    this.atualizarNotasSubject.next();
  }

  switchNotasCarregando(): void {
    if (this.notasCarregando = false) {this.notasCarregando = true}
    else {this.notasCarregando = false}
  }

  getNotasCarregandoEstado(): boolean {
    return this.notasCarregando
  }

  getAllMateriasHistoricas(): Materia[] {
    return this.historicas
  }

  getAllMateriasParciais(): Materia[] {
    return this.parciais
  }
  
  atualizaMateriasHistoricas(data: Materia[]): void {
    this.historicas = data;
  }
  atualizaMateriasParciais(data: Materia[]): void {
    this.parciais = data;
  }
}
