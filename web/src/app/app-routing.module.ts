import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { FullViewComponent } from "./component/full-view/full-view.component";
import { AppComponent } from "./app.component";

const routes: Routes = [
  {
    path: "_/:filter",
    component: AppComponent,
    pathMatch: "full"
  },
  {
    path: "photo/:id",
    component: FullViewComponent,
    pathMatch: "full"
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
