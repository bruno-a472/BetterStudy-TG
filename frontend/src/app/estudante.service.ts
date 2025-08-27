import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class EstudanteService {
  protected id = 0;

  constructor() { }

  defineId(id: number) {
    this.id = id;
  }

  obtemId(): number {
    return this.id;
  }

}
