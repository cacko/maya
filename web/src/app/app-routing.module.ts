import {NgModule} from "@angular/core";
import {RouterModule, Routes} from "@angular/router";
import {FullViewComponent} from "./component/full-view/full-view.component";
import {AppComponent} from "./app.component";

import {AngularFireAuthGuard, redirectLoggedInTo, redirectUnauthorizedTo,} from '@angular/fire/compat/auth-guard';
import {LoginComponent} from './component/login/login.component';

const redirectUnauthorizedToLogin = () => redirectUnauthorizedTo(['login']);
const redirectLoggedInToHome = () => redirectLoggedInTo(['']);

const routes: Routes = [
  {
    path: '',
    component: AppComponent,
    pathMatch: "full",
    canActivate: [AngularFireAuthGuard],
    data: {authGuardPipe: redirectUnauthorizedToLogin},
  },
  {
    path: 'photo/:id',
    component: FullViewComponent,
    pathMatch: "full",
    canActivate: [AngularFireAuthGuard],
    data: {authGuardPipe: redirectUnauthorizedToLogin},
  },
  {
    path: 'face/:face',
    component: AppComponent,
    pathMatch: "full",
    canActivate: [AngularFireAuthGuard],
    data: {authGuardPipe: redirectUnauthorizedToLogin},
  },
  {
    path: 'login',
    component: LoginComponent,
    pathMatch: 'full',
    canActivate: [AngularFireAuthGuard],
    data: {authGuardPipe: redirectLoggedInToHome},
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
