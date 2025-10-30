import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EstudantePerfilComponent } from './estudante-perfil.component';

describe('EstudantePerfilComponent', () => {
  let component: EstudantePerfilComponent;
  let fixture: ComponentFixture<EstudantePerfilComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EstudantePerfilComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EstudantePerfilComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
