import { Component } from '@angular/core';
import { NgIf } from '@angular/common';
import { DadosService } from '../dados.service';
import { Router } from '@angular/router';
import { EstudanteService } from '../estudante.service';

@Component({
  selector: 'app-sms',
  imports: [NgIf],
  templateUrl: './sms.component.html',
  styleUrl: './sms.component.scss'
})
export class SmsComponent {
  constructor(private router: Router,
              private dadosService: DadosService,
              private estudante: EstudanteService) {}
  visualizacao = false;

  id = 0;

  ngOnInit(): void {
    setTimeout(() => {
      this.visualizacao = true;
    }, 100);
  } // ngOnInit()

  confirmarLogin() {
    console.log('Clicado');

    const confirmacao =  {
      codigo: (document.getElementsByClassName('codigo')[0] as HTMLInputElement).value,
      id: this.estudante.obtemId()
    }
    console.log(confirmacao);
    this.dadosService.enviarConfirmacao(confirmacao).subscribe(resposta => {
      if (resposta['bool'] == false) {
        console.log('Confirmacao falhou')  
        // Confirmação falhou
      } // if
      else {
        this.router.navigate([`/${resposta['nome']}/atual`]);
      } // else
      
    }, // resposta =>
    erro => {
      console.error('Erro ao enviar dados:', erro);
    } // erro
    ); // subscribe()

  } // confirmarLogin()
}
