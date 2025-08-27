import { NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ActivatedRoute, RouterOutlet } from '@angular/router';
import { DadosService } from '../dados.service';
import { EstudanteService } from '../estudante.service';
import { MateriaService } from '../materia.service';

@Component({
  selector: 'app-bunker-notas',
  imports: [RouterOutlet, NgIf],
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
    this.pegarNotas();
    setTimeout(() => {
      this.visualizacao = true;
    }, 100);

  } // ngOnInit()

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
      } // else
    },
    erro => {
      console.error('Erro ao enviar dados:', erro);
    } // erro
  );} // pegarNotas()
  
}
