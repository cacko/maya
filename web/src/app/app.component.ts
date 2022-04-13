import {
  AfterViewInit,
  Component,
  ElementRef,
  HostListener,
  OnInit,
  TemplateRef,
  ViewChild,
  ViewContainerRef
} from "@angular/core";
import {AuthService} from "./service/auth.service";
import {SwUpdate, VersionReadyEvent} from "@angular/service-worker";
import {MatSnackBar} from "@angular/material/snack-bar";
import {filter, map, Subscription, timer} from "rxjs";
import {ImageService} from "./service/image.service";
import {ActivatedRoute, Router} from "@angular/router";
import {ViewportScroller} from "@angular/common";
import {FormBuilder, FormControl, FormGroup} from "@angular/forms";
import {Overlay, OverlayConfig, OverlayRef} from "@angular/cdk/overlay";
import {TemplatePortal} from "@angular/cdk/portal";
import {FaceService} from "./service/face.service";


enum SearchOriginator {
  BUTTON = 1,
  ESC = 2,
  ENTER = 3,
  SLASH = 4,
  INIT = 5,
  BACKDROP = 6,
}

const SEARCH_STATES = ["search", "search_off"];


@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"]
})
export class AppComponent implements OnInit, AfterViewInit {
  title = "app";
  page = 1;
  updating = true;
  selected: string | undefined | null = null;
  loading = true;
  throttle = 50;
  scrollDistance = 2;
  scrollUpDistance = 1.5;
  isHorizontal = false;
  form: FormGroup;
  query: string = "";
  isSearching = false;
  keywords: string[] = [];

  private keyboardInterval: Subscription | undefined;
  private overlayRef: OverlayRef | undefined;

  @ViewChild("search") searchInput: ElementRef | undefined;
  @ViewChild("searchForm") tpl: TemplateRef<any> | undefined;

  constructor(
    public auth: AuthService,
    public imageService: ImageService,
    private swUpdate: SwUpdate,
    private snackBar: MatSnackBar,
    private router: Router,
    private scroller: ViewportScroller,
    private route: ActivatedRoute,
    private viewportScroller: ViewportScroller,
    private builder: FormBuilder,
    private overlay: Overlay,
    private viewContainerRef: ViewContainerRef
  ) {
    if (this.swUpdate.isEnabled) {
      swUpdate.versionUpdates.pipe(
        filter((evt): evt is VersionReadyEvent => evt.type === "VERSION_READY"),
        map(evt => ({
          type: "UPDATE_AVAILABLE",
          current: evt.currentVersion,
          available: evt.latestVersion
        }))).subscribe((res) => {
        this.snackBar
          .open("Update is available", "Update")
          .onAction()
          .subscribe(() =>
            this.swUpdate
              .activateUpdate()
              .then(() => document.location.reload())
          );
      });
    }
    this.auth.isLogged.subscribe(res => {
      if (res) {
        this.loading = true;
        this.imageService.load().then(() => {
          this.loading = false;
        });
      }
    });
    this.form = this.builder.group({
      query: new FormControl()
    });
    this.imageService.loading.subscribe(val => {
      setTimeout(() => {
        this.loading = !!val;
      }, 0);
    });
    this.imageService.selected.subscribe((selected) => {
      if (!selected) {
        let commands  = [""];
        if (this.imageService.face) {
          commands = ["face", this.imageService.face];
        }
        this.router.navigate(commands).then(() => {
          this.imageService.endLoader();
        });
      } else {
        this.router.navigate(["photo", selected]).then(() => {});
      }
      setTimeout(() => {
        const oldId = this.selected;
        this.selected = selected;
        this.isHorizontal = !!selected;
        if (!selected && oldId) {
          setTimeout(() => {
            this.viewportScroller.scrollToAnchor(oldId + "");
          }, 0);
        }
      }, 0);
    });
  }

  ngAfterViewInit(): void {
    const positionStrategy = this.overlay
      .position()
      .global()
      .centerHorizontally()
      .centerVertically();
    const configs = new OverlayConfig({
      hasBackdrop: true,
      panelClass: ["search-overlay", "is-active"],
      backdropClass: "search-backdrop",
      positionStrategy
    });
    this.overlayRef = this.overlay.create(configs);
    this.overlayRef.backdropClick().subscribe(() => {
      this.hideSearch(SearchOriginator.BACKDROP);
    });
  };

  async ngOnInit() {
    this.route.params.subscribe((params) => {
      const face = params["id"] || "";
        setTimeout(() => {
          this.imageService.setFace(face);
          this.imageService.load().then(() => {
            this.imageService.endLoader();
          })
        }, 0);
    });

    this.form.get("query")?.valueChanges.subscribe((value: string) => {
      if (this.keyboardInterval && !this.keyboardInterval.closed) {
        this.keyboardInterval.unsubscribe();
      }
      this.keyboardInterval = timer(1000).subscribe(() => {
        value = value?.trim().toLowerCase() || "";
        if (this.query.length > 0 && this.query.length < 3) {
          return;
        }
        if (value != this.query) {
          this.query = value;
          this.doSearch(value);
        }
      });
      return false;
    });

  }

  async doSearch(filter: string) {
    this.query = filter;
    this.keywords = this.query.split(" ");
    this.imageService.setFilter(filter);
    if (filter.length) {
      await this.router.navigate([""], {queryParams: {filter}, replaceUrl: true});
    } else {
      await this.router.navigate([""], {replaceUrl: true});
    }
    // this.form.get("query")?.patchValue(filter);
    this.imageService.startLoader();
    await this.imageService.load().then(() => {
      this.imageService.endLoader();
    });
  }

  openWithTemplate(tpl: TemplateRef<any> | undefined) {
    if (!tpl) {
      return;
    }
    this.overlayRef?.attach(new TemplatePortal(tpl, this.viewContainerRef));
  }

  async onScrollDown() {
    await this.imageService.load();
  }


  @HostListener("document:keydown.enter", ["$event"])
  onEnter() {
    if (!this.isSearching) {
      return;
    }
    this.hideSearch(SearchOriginator.ENTER);
  }

  @HostListener("document:keydown.escape", ["$event"])
  onEscape() {
    if (this.selected) {
      this.imageService.unselect();
    }
  }

  showSearch(originator: SearchOriginator) {
    if (originator == SearchOriginator.BUTTON && this.query.length > 0) {
      this.resetSearch();
      return;
    }
    this.openWithTemplate(this.tpl);
    setTimeout(() => {
      this.searchInput?.nativeElement.focus();
      this.isSearching = true;
    }, 0);
  }

  hideSearch(originator: SearchOriginator) {
    this.isSearching = false;
    this.overlayRef?.detach();
  }

  get searchIcon(): string {
    return SEARCH_STATES[+(this.isSearching || this.query?.trim().length > 0)];
  }

  resetSearch() {
    this.form.get("query")?.reset();
    this.imageService.clear();
    this.imageService.startLoader();
    this.imageService.load().then(() => {
      this.imageService.endLoader();
    });
  }

  onSearch() {
    return this.isSearching
      ? this.hideSearch(SearchOriginator.BUTTON)
      : this.showSearch(SearchOriginator.BUTTON);
  }

  async removeKeyword(word: string) {
    this.keywords = this.keywords.filter(a => a != word);
    this.query = this.keywords.join(" ");
    await this.doSearch(this.query);
  }

}
