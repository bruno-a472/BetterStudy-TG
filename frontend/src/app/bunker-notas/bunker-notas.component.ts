import { NgIf } from '@angular/common';
import { Component, inject, ViewChild } from '@angular/core';
import { ActivatedRoute, RouterOutlet } from '@angular/router';
import { DadosService } from '../dados.service';
import { EstudanteService } from '../estudante.service';
import { MateriaService } from '../materia.service';
import { ChatComponent } from '../chat/chat.component';
import { firstValueFrom } from 'rxjs';

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

  @ViewChild(ChatComponent, { static: true }) chatComponent!: ChatComponent;

  visualizacao = false;
  async ngOnInit() {
    setTimeout(() => {
      this.visualizacao = true;
    }, 100);
    console.log("BunkerNotasComponent ngOnInit - ID do estudante:", this.estudanteService.obtemId());
    if (this.estudanteService.checarAmbienteTeste() === 1) {
      console.log('⚠️ Modo de teste ativado: carregando notas locais.');
      this.dadosService.obterNotasLocais().subscribe(resposta => {
        console.log('✅ Dados de notas locais carregados com sucesso:', resposta);
        this.materiaService.atualizaMateriasHistoricas(resposta['historicas'])
        this.materiaService.atualizaMateriasParciais(resposta['parciais'])
        this.materiaService.switchNotasCarregando(); // Service avisa que notas carregaram, trocando variável pra false
        localStorage.setItem('materiasHistoricas', JSON.stringify(resposta['historicas']));
        localStorage.setItem('materiasParciais', JSON.stringify(resposta['parciais']));

      });
      const perfilLS = localStorage.getItem('perfil_estudante_v1');
      const perfil = perfilLS ? JSON.parse(perfilLS) : null;
      console.log("Ambiente de teste obtendo relatório inicial");
      setTimeout(() => {
        this.estudanteService.solicitarRelatorioInicial(this.estudanteService.obtemId(), perfil);
      }, 2000);
      this.estudanteService.switchAmbienteTeste();
      console.log('⚠️ Modo de teste desativado após carregar notas locais.');
      return;
    }
    // Primeiro tenta carregar do localStorage
    const historicasLS = localStorage.getItem('materiasHistoricas');
    const parciaisLS = localStorage.getItem('materiasParciais');
    const perfilLS = localStorage.getItem('perfil_estudante_v1');

    const historicas = historicasLS ? JSON.parse(historicasLS) : null;
    const parciais = parciaisLS ? JSON.parse(parciaisLS) : null;
    const perfil = perfilLS ? JSON.parse(perfilLS) : null;

    if (historicas && historicas.length > 0 && parciais && parciais.length > 0) {
      console.log('✅ Dados carregados do localStorage');
      console.log(historicas);
      console.log(parciais);
      console.log(perfil);
      // Se tem algo no localStorage, carrega direto de lá
      this.materiaService.atualizaMateriasHistoricas(historicas);
      this.materiaService.atualizaMateriasParciais(parciais);
      this.materiaService.switchNotasCarregando();
    } else {
      // Se não tem nada no localStorage, busca no backend
      await this.pegarNotas();
    }
    console.log("Normalmente obtendo relatório inicial");
      console.log(this.estudanteService.obtemId());
      this.estudanteService.solicitarRelatorioInicial(this.estudanteService.obtemId(), perfil);
  }

  atualizaId() {
    this.estudanteService.defineId(3); // Teste
  }

  async pegarNotas(): Promise<void> {
    const id = {id: this.estudanteService.obtemId()} // Obtendo ID do estudante registrado no backend
    
    try {
      // Início da requisição HTTP
      const resposta = await firstValueFrom(this.dadosService.receberNotas(id))
      if (!resposta || resposta['bool'] === false) {
        console.log('Falhou ao obter notas do backend');
        return;
      }

      this.materiaService.atualizaMateriasHistoricas(resposta['historicas'])
      this.materiaService.atualizaMateriasParciais(resposta['parciais'])
      this.materiaService.switchNotasCarregando(); // Service avisa que notas carregaram, trocando variável pra false
    
      localStorage.setItem('materiasHistoricas', JSON.stringify(resposta['historicas']));
      localStorage.setItem('materiasParciais', JSON.stringify(resposta['parciais']));
    } catch(erro) { 
      console.error('Erro ao enviar dados:', erro);
    } // catch
  ;} // pegarNotas()

  limparCacheNotas(): void {
    // Remover do localStorage
    localStorage.removeItem('materiasHistoricas');
    localStorage.removeItem('materiasParciais');

    // Resetar no service (caso os dados já estejam em memória)
    this.materiaService.atualizaMateriasHistoricas([]);
    this.materiaService.atualizaMateriasParciais([]);
    this.materiaService.switchNotasCarregando(); // Reativa o estado "carregando"

    console.log('🧹 Cache de notas limpo com sucesso!');
  } // limparCacheNotas

  // testarChat(): void {
  //   this.estudanteService.solicitarRelatorioInicial(this.estudanteService.obtemId(), perfil);
  // }
}
