import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Mensagem } from './mensagem';

@Injectable({
  providedIn: 'root'
})
export class EstudanteService {
  private id = 0;
  // 3. Defina a URL base do seu backend para facilitar a manutenção
  private apiUrl = 'http://localhost:5000/api';

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

  iniciarChat(notas: any): Observable<{ relatorio_inicial: string }> {
    const body = {
      id_usuario: this.id, // Usa o ID armazenado no serviço
      notas: notas
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
}