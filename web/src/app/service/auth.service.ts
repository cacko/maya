import {Injectable} from "@angular/core";
import {Subject} from "rxjs";
import {AngularFireAuth} from "@angular/fire/compat/auth";
import firebase from 'firebase/compat/app';

@Injectable({
  providedIn: "root"
})
export class AuthService {

  private loggedSubject = new Subject<boolean>();
  isLogged = this.loggedSubject.asObservable();

  private userSubject = new Subject<firebase.User | null>();
  user = this.userSubject.asObservable();

  token: string = "";

  constructor(
    private auth: AngularFireAuth
  ) {
    this.auth.onIdTokenChanged((user) => {
      user?.getIdToken().then(token => {
        this.token = token + "";
      });
    }).then(() => {
    });
    this.auth.onAuthStateChanged((user) => {
      this.userSubject.next(user);
      this.loggedSubject.next(!!user && !user.isAnonymous);
    }).then(() => {
    });
  }

  logout() {
    return this.auth.signOut();
  }
}
