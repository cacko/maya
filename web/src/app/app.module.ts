import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { initializeApp, provideFirebaseApp } from "@angular/fire/app";
import { environment } from "../environments/environment";
import { getAuth, provideAuth } from "@angular/fire/auth";
import { AuthService } from "./service/auth.service";
import { ApiService } from "./service/api.service";
import { SETTINGS as AUTH_SETTINGS } from "@angular/fire/compat/auth";
import { AngularFireModule } from "@angular/fire/compat";
import { CardComponent } from "./component/card/card.component";
import { HttpClientModule } from "@angular/common/http";
import { InfiniteScrollModule } from "ngx-infinite-scroll";
import { ServiceWorkerModule } from "@angular/service-worker";
import { LoaderComponent } from "./component/loader/loader.component";
import { MatProgressBarModule } from "@angular/material/progress-bar";
import { MatSnackBarModule } from "@angular/material/snack-bar";
import { MatRippleModule } from "@angular/material/core";
import { MatButtonModule } from "@angular/material/button";
import { FullViewComponent } from "./component/full-view/full-view.component";
import { MatIconModule } from "@angular/material/icon";
import { MatInputModule } from "@angular/material/input";
import { ReactiveFormsModule } from "@angular/forms";
import { MatChipsModule } from "@angular/material/chips";
import { FolderComponent } from './component/folder/folder.component';
import { FaceComponent } from './component/face/face.component';
import { FacesComponent } from './component/faces/faces.component';
import {MatTooltipModule} from '@angular/material/tooltip';

const MATERIALS = [
  MatProgressBarModule,
  MatSnackBarModule,
  MatRippleModule,
  MatButtonModule,
  MatIconModule,
  MatInputModule,
  ReactiveFormsModule,
  MatChipsModule,
  MatTooltipModule
];

@NgModule({
  declarations: [
    AppComponent,
    CardComponent,
    LoaderComponent,
    FullViewComponent,
    FolderComponent,
    FaceComponent,
    FacesComponent
  ],
  imports: [
    BrowserModule,
    InfiniteScrollModule,
    ...MATERIALS,
    AppRoutingModule,
    HttpClientModule,
    BrowserAnimationsModule,
    AngularFireModule.initializeApp(environment.firebase),
    provideFirebaseApp(() => initializeApp(environment.firebase)),
    provideAuth(() => getAuth()),
    ServiceWorkerModule.register("ngsw-worker.js", {
      enabled: environment.production,
      // Register the ServiceWorker as soon as the application is stable
      // or after 30 seconds (whichever comes first).
      registrationStrategy: "registerWhenStable:30000"
    })
  ],
  providers: [
    {
      provide: AUTH_SETTINGS,
      useValue: { appVerificationDisabledForTesting: true }
    },
    AuthService,
    ApiService
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}
