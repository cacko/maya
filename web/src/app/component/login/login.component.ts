import {Component, OnInit} from '@angular/core';
import { AngularFireAuth } from '@angular/fire/compat/auth';
import firebase from '@firebase/app-compat';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnInit {
  constructor(public auth: AngularFireAuth) {
  }

  async login() {
    const provider = new firebase.auth.GoogleAuthProvider();
    provider.addScope('profile');
    provider.addScope('email');
    const user = await this.auth.signInWithRedirect(provider);
  }

  logout() {
    this.auth.signOut().then((res: any) => {
      console.log(res);
    });
  }

  ngOnInit(): void {
    this.login();
  }
}
