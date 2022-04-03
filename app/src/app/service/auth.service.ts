import { Injectable } from "@angular/core";
import { User, Auth } from "@angular/fire/auth";
import { Subject } from "rxjs";
import { AngularFireAuth } from "@angular/fire/compat/auth";

@Injectable({
  providedIn: "root"
})
export class AuthService {

  private loggedSubject = new Subject<boolean>();
  isLogged = this.loggedSubject.asObservable();

  constructor(
    private auth: Auth,
    private fireAuth: AngularFireAuth
  ) {
    console.log("auth service");
    this.auth.onAuthStateChanged((user: User | null) => {
      this.loggedSubject.next(!!user?.isAnonymous);
    });
    this.fireAuth.signInAnonymously().then((user) => {
      console.log(user);
      // this.loggedSubject.next(true);
    }).catch(e => {
      console.error((e));
    });
  }
}
