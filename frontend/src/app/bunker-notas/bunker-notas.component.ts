import { NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ActivatedRoute, RouterOutlet } from '@angular/router';
import { DadosService } from '../dados.service';
import { EstudanteService } from '../estudante.service';
import { MateriaService } from '../materia.service';
import { ChatComponent } from '../chat/chat.component';

@Component({
  selector: 'app-bunker-notas',
  imports: [RouterOutlet, NgIf, ChatComponent],
  templateUrl: './bunker-notas.component.html',
  styleUrl: './bunker-notas.component.scss'
})
export class BunkerNotasComponent {

  route: ActivatedRoute = inject(ActivatedRoute);
  nome = '';
  
  constructor(private dadosService: DadosService,
              private estudanteService: EstudanteService,
              private materiaService: MateriaService) {
    this.nome = this.route.snapshot.params['nome'] 
  }

  visualizacao = false;
  ngOnInit(): void {
    // Primeiro tenta carregar do localStorage
    const historicasLS = localStorage.getItem('materiasHistoricas');
    const parciaisLS = localStorage.getItem('materiasParciais');

    const historicas = historicasLS ? JSON.parse(historicasLS) : null;
    const parciais = parciaisLS ? JSON.parse(parciaisLS) : null;

    if (historicas && historicas.length > 0 && parciais && parciais.length > 0) {
      console.log('✅ Dados carregados do localStorage');
      console.log(historicas);
      console.log(parciais);
      // Se tem algo no localStorage, carrega direto de lá
      this.materiaService.atualizaMateriasHistoricas(historicas);
      this.materiaService.atualizaMateriasParciais(parciais);
      this.materiaService.switchNotasCarregando();
    } else {
      // Se não tem nada no localStorage, busca no backend
      this.pegarNotas();
    }

    setTimeout(() => {
      this.visualizacao = true;
    }, 100);
  }

  // ngOnInit(): void {
  //   this.pegarNotas();
  //   setTimeout(() => {
  //     this.visualizacao = true;
  //   }, 100);

  // } // ngOnInit()

  atualizaId() {
    this.estudanteService.defineId(3); // Teste
  }

  pegarNotas() {
    const id = {id: this.estudanteService.obtemId()} // Obtendo ID do estudante registrado no backend
    
    // Início da requisição HTTP
    this.dadosService.receberNotas(id).subscribe(resposta => {
      if (resposta['bool'] == false) { // Arrumar esse teste para caso haja return Vazio das notas
        console.log('Falhou')
      } // if
      else {
        this.materiaService.atualizaMateriasHistoricas(resposta['historicas'])
        this.materiaService.atualizaMateriasParciais(resposta['parciais'])
        this.materiaService.switchNotasCarregando(); // Service avisa que notas carregaram, trocando variável pra false
      
        localStorage.setItem('materiasHistoricas', JSON.stringify(resposta['historicas']));
        localStorage.setItem('materiasParciais', JSON.stringify(resposta['parciais']));

      } // else
    },
    erro => {
      console.error('Erro ao enviar dados:', erro);
    } // erro
  );} // pegarNotas()
  
}
