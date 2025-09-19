export interface Mensagem {
  chat_id: number;
  text: string;
  remetente: 'usuario' | 'bot';
  timestamp: Date;
}
