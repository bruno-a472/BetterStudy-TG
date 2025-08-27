import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { BunkerNotasComponent } from './bunker-notas/bunker-notas.component';
import { HistoricoComponent } from './historico/historico.component';
import { AtualComponent } from './atual/atual.component';
import { SmsComponent } from './sms/sms.component';

export const routes: Routes = [

    {
        path: '',
        redirectTo: '/login',
        pathMatch: 'full'
    },
    {
        path: 'login',
        component: LoginComponent,
        title: 'Login'
    },
    {
        path: 'login/confirmacao',
        component: SmsComponent,
        title: 'Login'
    },
    {
        path: ':nome',
        component: BunkerNotasComponent,
        title: '...',
        children: [
            {
                path: 'atual',
                component: AtualComponent,
                title: 'Atual'
            },
            {
                path: 'historico',
                component: HistoricoComponent,
                title: 'Historico'
            }
        ]
    },
    
    

];
