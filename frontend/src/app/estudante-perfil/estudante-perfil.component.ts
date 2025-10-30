import { Component, OnInit, ChangeDetectionStrategy,  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { EstudanteService } from '../estudante.service';
import { Router } from '@angular/router';

export interface FamiliaridadeMetodos {
  pomodoro: number;
  revisao_espacada: number;
  mapa_mental: number;
  aprendizado_ativo: number;
  aprendizado_passivo: number;
  flashcards: number;
}

export interface PerfilEstudante {
  familiaridade_metodos: FamiliaridadeMetodos;   // 1..5
  tipo_aprendiz: 'visual' | 'auditivo' | 'leitura_escrita' | 'cinestesico';
  nivel_foco: 'baixo' | 'medio' | 'alto';
  horas_estudo_dia: '15min' | '30min' | '1hr' | '>2hrs';
  motivacao_estudo: string;                      // texto livre
  atualizadoEm: string;                          // ISO string
}

const STORAGE_KEY = 'perfil_estudante_v1';

@Component({
  selector: 'app-estudante-perfil',
  templateUrl: './estudante-perfil.component.html',
  styleUrls: ['./estudante-perfil.component.scss'],
  imports: [CommonModule, ReactiveFormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class EstudantePerfilComponent implements OnInit {

  form!: FormGroup;

  tiposAprendiz = [
    { value: 'visual', label: 'Visual' },
    { value: 'auditivo', label: 'Auditivo' },
    { value: 'leitura_escrita', label: 'Leitura/Escrita' },
    { value: 'cinestesico', label: 'Cinestésico' },
  ] as const;

  niveisFoco = [
    { value: 'baixo', label: 'Baixo' },
    { value: 'medio', label: 'Médio' },
    { value: 'alto', label: 'Alto' },
  ] as const;

  faixasTempo = [
    { value: '15min', label: '15 min' },
    { value: '30min', label: '30 min' },
    { value: '1hr', label: '1 hora' },
    { value: '>2hrs', label: 'Mais de 2 horas' },
  ] as const;


  constructor(
    private fb: FormBuilder,
    private estudanteService: EstudanteService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // cria o form com valores padrão 3/mediano
    this.form = this.fb.group({
      familiaridade_metodos: this.fb.group({
        pomodoro: [3, [Validators.required, this.minMax(1, 5)]],
        revisao_espacada: [3, [Validators.required, this.minMax(1, 5)]],
        mapa_mental: [3, [Validators.required, this.minMax(1, 5)]],
        aprendizado_ativo: [3, [Validators.required, this.minMax(1, 5)]],
        aprendizado_passivo: [3, [Validators.required, this.minMax(1, 5)]],
        flashcards: [3, [Validators.required, this.minMax(1, 5)]],
      }),
      tipo_aprendiz: ['visual', Validators.required],
      nivel_foco: ['medio', Validators.required],
      horas_estudo_dia: ['30min', Validators.required],
      motivacao_estudo: ['', [Validators.required, Validators.minLength(8)]],
    });

    // carrega do localStorage (se existir)
    const salvo = localStorage.getItem(STORAGE_KEY);
    if (salvo) {
      try {
        const perfil: PerfilEstudante = JSON.parse(salvo);
        this.form.patchValue({
          familiaridade_metodos: perfil.familiaridade_metodos,
          tipo_aprendiz: perfil.tipo_aprendiz,
          nivel_foco: perfil.nivel_foco,
          horas_estudo_dia: perfil.horas_estudo_dia,
          motivacao_estudo: perfil.motivacao_estudo,
        });
      } catch {
        // se der erro de parsing, ignora e segue com defaults
      }
    }
  }

  // validator simples p/ sliders 1..5
  private minMax(min: number, max: number) {
    return (ctrl: any) => {
      const v = Number(ctrl.value);
      return v >= min && v <= max ? null : { range: true };
    };
  }

  salvar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const perfil: PerfilEstudante = {
      ...this.form.value,
      atualizadoEm: new Date().toISOString(),
    };

    // 1) salva localmente
    localStorage.setItem(STORAGE_KEY, JSON.stringify(perfil));

    const userId = this.estudanteService.obtemId();


    console.log('Salvo perfil para ID:', userId, perfil);
    console.log(`Navegando para /${this.estudanteService.obtemNome()}/atual`);
    this.router.navigate([`/${this.estudanteService.obtemNome()}/atual`]);

    alert('Perfil salvo com sucesso!');
  }

  limpar(): void {
    this.form.reset({
      familiaridade_metodos: {
        pomodoro: 3,
        revisao_espacada: 3,
        mapa_mental: 3,
        aprendizado_ativo: 3,
        aprendizado_passivo: 3,
        flashcards: 3,
      },
      tipo_aprendiz: 'visual',
      nivel_foco: 'medio',
      horas_estudo_dia: '30min',
      motivacao_estudo: '',
    });
    localStorage.removeItem(STORAGE_KEY);
  }
}
