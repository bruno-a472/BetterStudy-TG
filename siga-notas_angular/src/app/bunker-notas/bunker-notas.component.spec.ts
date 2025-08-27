import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BunkerNotasComponent } from './bunker-notas.component';

describe('BunkerNotasComponent', () => {
  let component: BunkerNotasComponent;
  let fixture: ComponentFixture<BunkerNotasComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BunkerNotasComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BunkerNotasComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
