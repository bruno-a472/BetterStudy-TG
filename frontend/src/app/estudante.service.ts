import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';

import { Mensagem } from './mensagem';

@Injectable({
  providedIn: 'root'
})
export class EstudanteService {
  private id = 0;
  private ambienteTeste = 0; // 0 = fluxo normal, 1 = fluxo de teste com dados locais
  // 3. Defina a URL base do seu backend para facilitar a manutenção
  private apiUrl = 'http://localhost:5000/api';

  private _initRelatorio$ = new Subject<number>();
  initRelatorio$ = this._initRelatorio$.asObservable();

  solicitarRelatorioInicial(userId: number) {
    this._initRelatorio$.next(userId);
  }

  constructor(private http: HttpClient) { }

  defineId(id: number) {
    this.id = id;
  }

  obtemId(): number {
    return this.id;
  }
  /**
   * 5. Envia os dados das notas para o backend para iniciar a sessão e obter o relatório inicial do LLM.
   * @param notas O objeto JSON com as notas parciais e históricas.
   * @returns Um Observable com a resposta do endpoint /init.
   */
  obterNotasLocais(): Observable<any> {
    // O Angular sabe servir arquivos da pasta 'assets' diretamente.
    return this.http.get<any>('assets/resultado_notas_12.json');
  }

  iniciarChat(id:number): Observable<{ relatorio_inicial: string }> {
    console.log('Iniciando chat para o ID:', id);
    const body = {
      id_usuario: id, // Usa o ID armazenado no serviço
    };
    return this.http.post<{ relatorio_inicial: string }>(`${this.apiUrl}/init`, body);
  }

  /**
   * 6. Envia uma nova mensagem do usuário para o backend e recebe a resposta do LLM.
   * @param texto A mensagem que o usuário digitou.
   * @returns Um Observable contendo a resposta do bot no formato da interface Mensagem.
   */
  enviarMensagem(texto: string): Observable<Mensagem> {
    const body = {
      chat_id: this.id, // Usa o ID armazenado no serviço
      text: texto
    };
    return this.http.post<Mensagem>(`${this.apiUrl}/chatbot`, body);
  }

  switchAmbienteTeste(): void {
    if (this.ambienteTeste === 0) {
      this.ambienteTeste = 1;
    } else {
      this.ambienteTeste = 0;
    }
  }

  checarAmbienteTeste(): number {
    return this.ambienteTeste;
  }
}