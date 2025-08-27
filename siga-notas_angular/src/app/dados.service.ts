import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DadosService {
  private apiUrlLogin = 'https://siga-notas-full-stack.onrender.com/api/login'; // URL login
  private apiUrlConfirmacao = 'https://siga-notas-full-stack.onrender.com/api/login/confirmacao'; // URL confirmação
  private apiUrlNotas = 'https://siga-notas-full-stack.onrender.com/api/notas'; // URL notas

  constructor(private http: HttpClient) { }

  enviarLogin(dados: any): Observable<any> {
    return this.http.post<any>(this.apiUrlLogin, dados);
  }
  
  enviarConfirmacao(dados: any): Observable<any> {
    return this.http.post<any>(this.apiUrlConfirmacao, dados);
  }
  
  receberNotas(dados: any): Observable<any> {
    return this.http.post<any>(this.apiUrlNotas, dados);
  }

}