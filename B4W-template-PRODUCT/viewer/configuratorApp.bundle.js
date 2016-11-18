(function () {"use strict";

  /**
   * @name configuratorApp
   * @author tsyganov.andrey@triumph.msk.ru (113)
   * @description 
   * Ru Модуль конфигуратор 3д предметов.
   * En Module configurator 3d items.
   */
  angular.module("configuratorApp", []);

}());
(function () {'use strict';
  
  /**
   * @description 
   * |En| Factory of 3d-objects available for configuration.
   * |Ru| Фабрика 3д объектов доступных для конфигурации.
   */
  angular.module('configuratorApp').factory('configuratorObject3d', configuratorObject3d);
  function configuratorObject3d (b4wCanvas, targetOfEdit, priceService,$q) {

    /**
     * @description 
     * |En| Registry of all registred 3d-objects available for configuration.
     * |Ru| Регистр всех зарегистрированных 3д-объектов доступных для конфигурации.
     * @type {Array} registry
     */
    var registry = [];

    /**
     * @description 
     * |En| Getting all 3d-objects from registry.
     * |Ru| Получить все 3д-объекты из регистра.
     * @return {Array} 
     */
    _Object3d.getAll = function () {
      return registry;
    };

    /**
     * @description 
     * |En| Search object in registry by name.
     * |Ru| Находим объект в регистре по имени.
     * @param  {String} name 
     * @return {Object}
     */
    _Object3d.getByName = function (name) {
      return registry.filter(function (item) {
        return item.name === name;
      })[0];
    };

    /**
     * @description 
     * |En| Search object in registry by 3d-object name.
     * |Ru| Находим объект в регистре по имени его 3д-объекта.
     * @param  {String} name 
     * @return {Object}
     */
    _Object3d.getByObjectName = function (objectName) {
      return registry.filter(function (item) {
        return item.objectName === objectName;
      })[0];
    };

    /**
     * @description 
     * |En| Search active 3d-object in active section.
     * |Ru| Находим активный 3д-объект в активной секции.
     * @return {Object} [description]
     */
    _Object3d.getPickedInSection = function (section) {
      return section.reduce(function (result, item) {
        return item.picked ? item : result;
      });
    };

    /**
     * @description 
     * |En| Getting all picked object in all sections.
     * |Ru| Получение всех выбранных объектов во всех секциях.
     * @return {Array} 
     */
    _Object3d.getAllPicked = function () {
      return registry.filter(function (item) {
        return item.picked;
      });
    };

    /**
     * @param  {[type]} type [description]
     * @return {Array}      [description]
     */
    _Object3d.getByType = function (type) {
      return registry.filter(function (item) {
        return item.type === type;
      });
    };
     /**
     * @param  {[type]} type [description]
     * @return {Array}      [description]
     */
    _Object3d.getByTypeFilter = function (type) {
      return registry.filter(function (item) {
        return item.type != type;
      });
    };
    /**
     * @description
     * |En| Getting collection 3d-objects by name of parent.
     * |Ru| Полуение коллекции 3д-объектов по имени родителя.
     * @param  {String} parentName 
     * @return {Array}
     */
    _Object3d.getByParentName = function (parentName) {
      return registry.filter(function (item) {
        return item.parent.name === parentName;
      });
    }

    /**
     * @description 
     * |En| Constructor of 3d objects.
     * |Ru| Конструктор 3д-обектов.
     * @param {Object} data   Базовые данные необходимые для создания экзепляра.
     * @param {Object <configuratorSection>} parent Родительская секция (Секция к которой принадлежит экземпляр).
     */
    function _Object3d (data, parent) {

      console.log('_Object3d',data);

      this.data       = data;
      this.name       = data.name;
      this.title      = data.title;
      this.user_image      = data.user_image;
      this.type       = parent.type;
      this.img        = data.img;
      this.exceptions = data.exceptions;

      this.color        = [0.61, 0.39, 0.07];
      this.materialName = '';
      this.objectName   = this.name + '.' + this.materialName;

      /**
       * |En| Selected are object.
       * |Ru| Выбран ли объект.
       * @type {Boolean}
       */
      this.picked = data.default;

      /**
       * |En| Whether is object in the exceptions.
       * |Ru| Находится ли объект в исключениях.
       * @type {Boolean}
       */
      this.excluded = false;

      /**
       * |En| Belonging to the section.
       * |Ru| Принадлежность к секции.
       */
      this.parent = parent;

      /**
       * |En| Writing instance at local registry.
       * |Ru| Записываем экзепляр в локальный регистр.
       */
      registry.push(this);
    }

    /**
     * @description
     * |En| Pick 3d-object.
     * |Ru| Выбор 3д-объекта.
     * @return {[type]} [description]
     */
    _Object3d.prototype.pick = function () {
      this.unpickAll();
      this.picked = true;
      b4wCanvas.showObject(this.objectName);
      this.applyExceptions();
      priceService.summarize(_Object3d.getAllPicked());
    };

    /**
     * @description 
     * |En| Change state of 3d-object at not active state and hide him in 3d-scene.
     * |Ru| Переводим 3д-оьъект в неактивное состояние и скрываем его в 3д-сцене.
     * @return {[type]} [description]
     */
    _Object3d.prototype.unpickAll = function () {
      var _section   = _Object3d.getByParentName(this.parent.name);
      var _picked    = _Object3d.getPickedInSection(_section);
      _picked.picked = false;
      b4wCanvas.hideObject(_picked.objectName);
    };

    /**
     * @description 
     * |En| Change color of 3d-object.
     * |Ru| Изменение цвета 3д-объекта.
     * @param {Array} color
     */
    _Object3d.prototype.setColor = function (color) {
      this.color = color;
      b4wCanvas.setColor(this.objectName, color);
    };

    /**
     * @description 
     * |En| Change property of material 3d-object.
     * |Ru| Изменение свойств материала 3д-объекта.
     * @param {String} material
     */
    _Object3d.prototype.setMaterial = function (material, color) {
      if (this.material !== material) {
        this.material = material;
      } else {
        return b4wCanvas.setColor(this.objectName, color);
      }

      this.materialName = material;

      b4wCanvas.hideObject(this.objectName);
      var splited = this.objectName.split('.')[0];
      var __objectName = splited + '.' + material;
    
      this.objectName = __objectName;
      b4wCanvas.showObject(this.objectName);
      b4wCanvas.setColor(this.objectName, color);

      /**
       * Обновляем стоимость.
       */
      this.price = priceService.getPrice(this.name, this.materialName);
      priceService.summarize(_Object3d.getAllPicked());
    };

    /**
     * @description
     * Exclude material.
     * @return {[type]} [description]
     */
    _Object3d.prototype.isExcluded = function (materialName) {
      var _bool = true;
      this.exceptions.materials.forEach(function (excludedMaterial) {
        if (excludedMaterial === materialName) {
          _bool = false;
        }
      });

      return _bool;
    };

    /**
     * @description 
     * |En| Apply exceptions.
     * |Ru| Актуализируем исключения.
     */
    _Object3d.prototype.applyExceptions = function () {
      var allObjects      = _Object3d.getAll();
      var allPicked       = _Object3d.getAllPicked();

      allObjects.map(function (item) {
        item.excluded = false;
      });

      var excludedObjectsArr = allPicked.map(function (item) {
        return item.exceptions.objects;
      });

      var excludedObjects = excludedObjectsArr.reduce(function (result, item) {
        return result ? result.concat(item) : item;
      }, 0);

      excludedObjects.forEach(function (excluding) {
        _Object3d.getByName(excluding).excluded = true;
      });
    };

    /**
     * @description 
     * |Ru| Получаем превью изображение для объектов с типом материал. 
     */
    _Object3d.prototype.getPreviewImg = function (timeout) {
      b4wCanvas.createPreviewImg(this, timeout);
    };


      /**
     * @description 
     * |Ru| Получаем превью изображение для объектов . 
     */
    _Object3d.prototype.getPreviewImgObjects = function (baseObject,timeout) {
       var deferred = $q.defer();  
 

      b4wCanvas.createPreviewImgObjects(this,baseObject, timeout);
      return deferred.resolve();
    };

    /**
     * @description 
     * |Ru| Задаём объекту имя материала установленного по умолчанию.  
     */
    _Object3d.prototype.setMaterialName = function () {
      var materials    = _Object3d.getByType('material');
      var _object      = b4wCanvas.m_scenes.get_object_by_name(materials[0].name);
      var materialName = b4wCanvas.m_material.get_materials_names(_object)[0];

      this.materialName = materialName;
      this.objectName   = this.name + '.' + this.materialName;
    };

    /**
     * @description
     * |Ru| Устанавливаем стоимость товара.
     */
    _Object3d.prototype.setPrice = function () {
      this.price    = priceService.getPrice(this.name, this.materialName);
      this.currency = priceService.getCurrency();
    };

    return _Object3d;
  }
}());
(function () {'use strict';
  
  /**
   * @description 
   * |En| Factory of sections.
   * |Ru| Фабрика секций.
   */
  angular.module('configuratorApp').factory('configuratorSection', configuratorSection);
  function configuratorSection (configuratorObject3d) {

    /**
     * @description 
     * |En| Registry of all created sections.
     * |Ru| Регистр всех созданных секций.
     * @type {Array} registry
     */
    var registry = [];

    /**
     * @description
     * |En| Getting all section from registry.
     * |Ru| Получить все секиции из регистра.
     * @return {Array} 
     */
    _Section.getAll = function () {
      return registry;
    };

    /**
     * @description
     * |En| Get material collection from section collection. 
     * |Ru| Получение коллекции материалов из коллекции секций. 
     * @return {Array} 
     */
    _Section.getMaterials = function () {
      return registry.filter(function (section) {
        return section.type === 'material';
      });
    };

    /**
     * @description 
     * |En| Constructor of section.
     * |Ru| Конструктор секций.
     * @param {Object} data 
     */
    function _Section (data) {
      this.data  = data;
      this.name  = data.name;
      this.title = data.title;
      this.type  = data.type;

      /**
       * @type {Array} items Массив всех принадлежащих секции типизированных 3д-оъектов. 
       */
      this.items = [];
      this.setObjects3d(data.items);

      /**
       * |En| Writing instance at local registry.
       * |Ru| Записываем экзепляр в локальный регистр.
       */
      registry.push(this);
    }

    /**
     * @description 
     * |En| Create typed essences of 3d-objects.
     * |Ru| Создаём типизированные сущности 3д-объектов. 
     * @param {Arrat} items 
     */
    _Section.prototype.setObjects3d = function(items) {
      if (items.length) {
        this.items = items.map(function (item) {
          return new configuratorObject3d(item, this);
        }.bind(this));
      }
    };

    return _Section;
  }
}());
(function () {'use strict';

  /**
   * @description
   * |En| Servis for control of canvas, with help b4w library.
   * |Ru| Сервис для управления canvas'ом при помощи библиотеки b4w. 
   */
  angular.module('configuratorApp').service('b4wCanvas', b4wCanvas);
  function b4wCanvas ($q, $location) {

    this.siteId = null;
    this.oid    = null; 

    /**
     * Connect b4w modules.
     */
    this.m_app       = b4w.require('app');
    this.m_data      = b4w.require('data');
    this.m_scenes    = b4w.require('scenes');
    this.m_camera    = b4w.require('camera');
    this.m_objects   = b4w.require('objects');
    this.m_container = b4w.require('container');
    this.m_preloader = b4w.require('preloader');
    this.m_mouse     = b4w.require('mouse');
    this.m_main      = b4w.require('main');
    this.m_material  = b4w.require('material');
    this.m_trans     = b4w.require('transform');

    /**
     * @description 
     * |En| Getting path on json of 3d-model and decoding url.
     * |Ru| Получение ссылки на json 3д-моделм и декодирование url'a. 
     * @return {String} path
     */
    this.getPath = function () {
      if ($location.url().length) {
        var url = $location.url().split('?load=');
      } else {
        var url = location.search.split('?load=');
      }

      if (url.length <= 1) {
        var path = 'b4wData/room-9/logo.json';
      } else {
        var result = url[1].split('&');
        var path = decodeURIComponent(result[0].replace(/\+/g,  " "));
      }
      // var path = '/userdata/' + this.oid + '/sites/' + this.siteId + '/b4wData/room-8/logo.json';
      return path;
    };

    /**
     * @description 
     * |En| Loading 3d-model in scene.
     * |Ru| Загрузка 3д-модели в сцене.
     * @returns {Promise} [description]
     */
    this.load = function () {
      var defer = $q.defer();

      function test () {
        this.m_preloader.create_preloader({
          container_color:"#fff",
          bar_color:"#ddd",  
          frame_color: "#009eff",
          font_color: "#009eff"
        });
        this.m_data.load(this.getPath(), this.loadCallback.bind(this, defer), this.preloaderCallback.bind(this), false, true);
      }

      test.call(this);
      return defer.promise;
    };

    /**
     * @description 
     * |En| Callback of initializaion scope drawing.
     * |Ru| Колбек инициализации области отрисовки.
     */
    this.loadCallback = function (defer) {
      this.showBase();
      this.m_app.enable_camera_controls();
      this.setCamLimits();
      defer.resolve();
    };

    /**
     * @description
     * |En| Create and start preloader.
     * |Ru| Создаём и запускаем прелодер.
     * @param  {Number} percentage
     */
    this.preloaderCallback = function (percentage) {
      this.m_preloader.update_preloader(percentage);
    }

    /**
     * @description 
     * |En| Show 3d-object with name 'base'
     * |Ru| Показываем 3д-объект с именем 'base'
     */
    b4wCanvas.prototype.showBase = function () {
      var _object = this.m_scenes.get_object_by_name('floor');
      this.m_scenes.show_object(_object);
    };

    /**
     * @description 
     * |En| Show 3d-objects default.
     * |Ru| Отображаем 3д-объекты по умолчанию.
     */
    b4wCanvas.prototype.showDefault = function (defaultObjects) {
      defaultObjects.forEach(function (item) {
        var _object = this.m_scenes.get_object_by_name(item.objectName);
        this.m_scenes.show_object(_object);
      }.bind(this));
    };
        /**
     * @description 
     * |En| Hide 3d-objects default.
     * |Ru| Отображаем 3д-объекты по умолчанию.
     */
    b4wCanvas.prototype.hideDefault = function (defaultObjects) {
      defaultObjects.forEach(function (item) {
        var _object = this.m_scenes.get_object_by_name(item.objectName);
        this.m_scenes.hide_object(_object);
      }.bind(this));
    };


    /**
     * @description
     * |En| Enable camera limits
     * |Ru| Включение лимитов в камере. 
     */
    b4wCanvas.prototype.setCamLimits = function () {
      var camObj = this.m_scenes.get_active_camera();
      this.m_camera.target_set_vertical_limits(camObj, {"down":6.3, "up":5.5});
      this.m_camera.target_set_distance_limits(camObj, {"min":5, "max":25});
      this.m_camera.target_switch_panning(camObj, false);
    };

    /**
     * @description 
     * |En|
     * |Ru| Делаем видимым объект в 3д-сцене.
     * @param {String} objectName 
     */
    b4wCanvas.prototype.showObject = function (objectName) {
      var _object3d = this.m_scenes.get_object_by_name(objectName);
      this.m_scenes.show_object(_object3d);
    };

    /**
     * @description
     * |En|
     * |Ru| Делаем невидимым модель в 3д-сцене.
     * @param {String} objectName
     */
    b4wCanvas.prototype.hideObject = function (objectName) {
      var _object3d = this.m_scenes.get_object_by_name(objectName);
      this.m_scenes.hide_object(_object3d);
    };

    /**
     * @description 
     * |En| Switch color for 3d-object.
     * |Ru| Смена цвета у 3д-объекта.
     * @param {String} objectName 
     * @param {Array}  color
     */
    b4wCanvas.prototype.setColor = function (objectName, color) {
      var _object3d = this.m_scenes.get_object_by_name(objectName);
      this.m_objects.set_nodemat_rgb(_object3d, [objectName, "RGB"],   color[0], color[1], color[2]);
    };

    /**
     * @description
     * |En| Switch material of 3d-object.
     * |Ru| Смена материала 3д-объекта.
     * @param {String} objectName 
     * @param {String} materialName
     */
    b4wCanvas.prototype.setMaterial = function (objectName, materialName) {
      var fullName = objectName + '_' + materialName;
      this.showObject(fullName);
      var _object3d = this.m_scenes.get_object_by_name(fullName);

      this.setColor(this.colorOfClothing);
    };

    /**
     * @description 
     * |Ru| Назначаем в переменную DOM-элемент <canvas>  
     * @param {<canvas>DOM} canvasElement
     */
    b4wCanvas.prototype.setCanvasElement = function (canvasElement) {
      this.canvasElement = canvasElement;
    };

        /**
     * @description 
     * 
     * @param {DOM<canvas>} canvasElement
     */
    b4wCanvas.prototype.createPreviewImgObjects = function (objectInst,baseObject, timeout) {
      var deferred = $q.defer();  
      var _object = this.m_scenes.get_object_by_name(objectInst.objectName);
      var _objectBase = this.m_scenes.get_object_by_name(baseObject.objectName);  

      setTimeout(function () {
        this.m_scenes.show_object(_object);
        this.m_scenes.show_object(_objectBase);


        setTimeout(function () {
          var cb = function(data) {
            objectInst.img = data
          }
            this.m_main.canvas_data_url(cb);
         // objectInst.img = this.canvasElement.toDataURL("image/png");
          setTimeout(function () {
            if(_object != _objectBase) {
                this.m_scenes.hide_object(_object);
            }

          
            deferred.resolve();
          //  this.m_scenes.hide_object(_objectBase);
          }.bind(this), 300);
        }.bind(this), 200);
      }.bind(this), timeout*1000/2);


       return deferred.promise;
      };

     /**
     * @description 
     * 
     * @param {DOM<canvas>} canvasElement
     */
    b4wCanvas.prototype.createPreviewImg = function (objectInst, timeout) {
      var _object = this.m_scenes.get_object_by_name(objectInst.name);
      this.m_trans.set_scale(_object, 10);

      setTimeout(function () {
        this.m_scenes.show_object(_object);
        setTimeout(function () {

            var cb = function(data) {

            objectInst.img = data
          }
            this.m_main.canvas_data_url(cb);
          
          // objectInst.img = this.canvasElement.toDataURL();
          setTimeout(function () {
            this.m_scenes.hide_object(_object);
          }.bind(this), 300);
        }.bind(this), 200);
      }.bind(this), timeout*1000/2);

      };  

    b4wCanvas.prototype.cameraControlOff = function () {
      this.m_app.disable_camera_controls();
    };

    b4wCanvas.prototype.cameraControlOn = function () {
      this.m_app.enable_camera_controls();
    };

  }

}());
(function () {'use strict';

  /**
   * @description 
   * |En| This is service for storing and transmit target(essence of <configuratorObject3d>) of edit.
   * |Ru| Это сервис для хранения и передачи цели(экземпляр <configuratorObject3d>) редактирования.
   */
  angular.module('configuratorApp').service('targetOfEdit', targetOfEdit);
  function targetOfEdit () {

    /**
     * @type {Object|null} target Редактируемый 3д-объект.
     */
    var target = null;

    /**
     * @property {Object<configuratorObject3d>|null} target Редактируемый 3д-объект.
     */
    Object.defineProperty(this, 'target', {
      get: function () {return target;},
      set: function (value) {target = value;}
    });

  }
}());
(function () {'use strict';

  /**
   * @description
   * Сервис для работы с коталогом цен.   
   */
  angular.module('configuratorApp').service('priceService', priceService);
  function priceService ($http, $location, b4wCanvas) {


    /**
     * @property {Float} currentPrice Стоимость всех выбранных товаров.
     */
    this.currentPrice = 0.00;

    this.prices = [];

    /**
     * @descripition
     * Получаем каталог цен.
     */
    $http.get('prices.json').then(function (response) {
      this.data     = response.data;
      this.currency = this.data.currency;
      this.prices   = this.data.items;
    }.bind(this));


    priceService.prototype.getWantengerPrices = function () {
      var oid    = b4wCanvas.oid;
      var siteId = b4wCanvas.siteId;
      var _APIServer = 'http://192.168.89.190:8008';
      // var _APIServer = !!window.location.hostname.match(/demo.wantenger/) ? 'http://api.demo.wantenger.com' 
                   // : (!!window.location.hostname.match(/wantenger/) ? 'http://release.wantenger.com' : 'http://api.demo.wantenger.com');

      $http.get(_APIServer + '/api/showcase/data_collection?storeName=boxes&siteId=' + siteId + '&oid=' + oid).then(function (response) {
        return response.data[0].products;
      })
      .then(function (products3d) {
        $http.get(_APIServer + '/api/terminal/products/?pager=1-100&org=' + oid).then(function (response) {
          this.currency = response.data[0].currency;
          var products  = response.data; 
          this.prices   = this.getTypedCollectionOfPrices(products3d, products);
        }.bind(this));
      }.bind(this));
    };

    /**
     * @description 
     * Create typed collection of prices.
     * @param  {Object} products3d 
     * @param  {Array}  products   
     * @return {Array} _pricesArr Typed collection of price.
     */
    priceService.prototype.getTypedCollectionOfPrices = function (products3d, products) {
      var _pricesArr = [];

      Object.keys(products3d).forEach(function (objectName) {
        var _objectName  = objectName.split('.')[0];
        var materialName = objectName.split(_objectName + '.')[1];
        var productId    = products3d[objectName].productId;
        var _price       = '0';

        products.forEach(function (item) {
          if (item.productId === productId) {
            _price = item.price;
          }
        });

        _pricesArr.push({name: _objectName, material: materialName, price: +_price});
      }.bind(this));
      
      return _pricesArr;
    };

    /**
     * @description
     * Получаем стоимость объекта
     * @param  {String} name [description]
     * @return {String} 
     */
    priceService.prototype.getPrice = function (objectName, materialName) {
      var coincidences = this.prices.filter(function (item) {
        return item.name === objectName;
      });

      return coincidences.filter(function (item) {
        return item.material === materialName;
      })[0].price;
    };

    /**
     * @description
     * Получаем тип используемой валюты.
     * @return {String}
     */
    priceService.prototype.getCurrency = function () {
      return this.сurrency;
    };

    /**
     * @description
     * Подсчёт общей стоимости конфигурируемоего товара.  
     * @param  {Array} objects [description]
     * @return {} 
     */
    priceService.prototype.summarize = function (pickedObjects) {
      var summ = null;
      pickedObjects.forEach(function (item) {
        if (summ) {
          summ = summ + item.price;
        } else {
          summ = item.price;
        }
      }.bind(this));

      this.currentPrice = summ;
    };
  }

}());
(function () {'use strict';

  /**
   * @desctiption
   * |En| Directive for control canvas element.
   * |Ru| Директива для взаимодействия с элементом canvas.
   */
  angular.module('configuratorApp').directive('configuratorCanvas', configuratorCanvas);
  function configuratorCanvas () {
    return {
      restrict: 'E',
      // templateUrl: 'angularApp/directives/configuratorCanvas/configuratorCanvas.html',
      template: '<div id="main_canvas_container"></div><div id="preloader_container"><div id="logo_container"><div id="preloader_caption">0%</div></div><div id="load_container"><div id="first_stage"></div><div id="second_stage"></div><div id="third_stage"></div></div><div id="circle_wrapper"><div id="circle_container"></div></div></div>',
      controller: 'configuratorCanvasController', controllerAs: 'canvas'
    }
  }
 
  /**
   * @description 
   * |En| Controller of directive configuratorCanvas.
   * |Ru| Контроллер директивы configuratorCanvas
   */
  angular.module('configuratorApp').controller('configuratorCanvasController', configuratorCanvasController);
  configuratorCanvasController.$inject = [
    '$q',
    '$http',
    '$scope', 
    '$rootScope', 
    '$timeout',
    'b4wCanvas', 
    'targetOfEdit', 
    'priceService',
    'configuratorObject3d', 
    'configuratorSection'
  ];
  function configuratorCanvasController (
    $q,
    $http,
    $scope, 
    $rootScope, 
    $timeout,
    b4wCanvas, 
    targetOfEdit, 
    priceService,
    configuratorObject3d, 
    configuratorSection
  ) {

    /**
     * b4w modules.
     */
    this.m_app       = b4wCanvas.m_app;
    this.m_data      = b4wCanvas.m_data;
    this.m_camera    = b4wCanvas.m_camera;
    this.m_scenes    = b4wCanvas.m_scenes;
    this.m_container = b4wCanvas.m_container;
    this.m_mouse     = b4wCanvas.m_mouse;
    this.m_objects   = b4wCanvas.m_objects;

    /**
     * @description
     * |En| Configs 3d-application.
     * |RU| Предустановки 3д-преложения.
     * @type {Object}
     */
    this.initConfig = {
      canvas_container_id: 'main_canvas_container',
      alpha: true,
      enable_selectable: true,
      background_color: new Float32Array([1,1,1]), 
      prevent_caching: false,
      autoresize: true
    };

    $scope.$watch('showPreloader', function(newValue, oldValue) {


    if(typeof(oldValue) != "undefined") {

      if(!newValue) {
             var delaultObjects = configuratorObject3d.getAllPicked();
      
      b4wCanvas.showDefault(delaultObjects);
      }
 
    //  b4wCanvas.m_container.resize_to_container()

    }
    });

    this.getConfPath = function () {
      var path = '/userdata/' + b4wCanvas.oid + '/sites/' + b4wCanvas.siteId + '/conf.json';
      return path;
    };

    /**
     * @description 
     * |En| Initialization of scope drawing 3d application.
     * |Ru| Инициализация области отрисовки 3д-приложения.
     */
       this.init = function () {
      this.m_app.init(angular.extend(this.initConfig, {
        callback: function (canvasElement) {
          b4wCanvas.load()
          .then(function () {

            /**
             * Получаем данные о 3д-объектах и создаём секции.
             */
            $http.get('conf.json').then(function (response) {
              this.export_wantenger = response.data.export_wantenger; 
              this.setSections(response.data.items);
            }.bind(this));
          }.bind(this))
          .then(function () {

            b4wCanvas.setCanvasElement(canvasElement);
            /**
             * Запускаем механизм создания скриншотов для превью изображений.
             */

          }.bind(this))
          .then(function () {

            /**
             * Назначаем имена материалов и стоимость для всех доступных объектов.
             */
            $timeout(function() {
              var all = configuratorObject3d.getByType('');
              all.forEach(function (_object) {
                _object.setMaterialName();
                _object.setPrice();
              });
            }, 100);
          }.bind(this))
          .then(function () {
            /**
             * Делаем видимыми объекты и запускаем слушатель клика по 3д-объектам.
             */
            $timeout(function () {
              var delaultObjects = configuratorObject3d.getAllPicked();
              priceService.summarize(delaultObjects);
              b4wCanvas.showDefault(delaultObjects);
              b4wCanvas.hideDefault(delaultObjects);
             
              this.listenerActivation(canvasElement);
            }.bind(this), 100);
          }.bind(this)).then(function () { 

              // var request2 = $timeout(function(){ return {type: 'obj2'}; });

            var deferred = $q.defer();  



            $timeout(function () {

              var materials = configuratorObject3d.getByType('material');
              //this.startPreloder(materials.length+13);
              this.startPreloder(1);
              console.log('materials',materials)

              // materials.forEach(function (_object, key) {
              //   if(!_object.user_image) {
              //   _object.getPreviewImg(key + 10);
              //   }
              // });

              var objects = configuratorObject3d.getByTypeFilter('material');

              console.log('objects',objects)
              var baseObject = objects.filter(function(e) {
                return e.name == "base"
              })[0]

              //   objects.forEach(function (_object, key) {
              //     if(!_object.user_image) {
              //   _object.getPreviewImgObjects(baseObject,key + 1);
              //     }
              // });

                  deferred.resolve();

            }.bind(this), 300)


           
             return deferred.promise;

          }.bind(this));
        }.bind(this)
      }));
    };

    /**
     * @description
     * |En| Set section collection.
     * |Ru| Присваиваем коллекцию секций.
     * @param {Array} mainData
     */
    this.setSections = function (dataOfSections) {
      dataOfSections.map(function (_section) {
        return new configuratorSection(_section);
      });
    };

    /**
     * @description 
     * |En| Activate listner of click on scope drawing.
     * |Ru| Активируем слушатель клика по области отрисовки(canvas).
     * @param {Element<canvas>}  canvasElement
     */
    this.listenerActivation = function (canvasElement) {
      canvasElement.addEventListener('mousedown', this.listenerCallback.bind(this), false);
      canvasElement.addEventListener('touchstart', this.listenerCallback.bind(this), false);
      this.canvasElement = canvasElement;
    };

    /**
     * @description 
     * |En| Find 3d-object by click point.
     * |Ru| Ищем 3д-объект в точке где был совершен клик. 
     * Если находим выбираем его и открываем панель редактирования материалов. 
     * @param  {Object} event 
     */
    this.listenerCallback = function (event) {
      if (event.preventDefault) {
        event.preventDefault();
      }

      var y = this.m_mouse.get_coords_y(event);
      var x = this.m_mouse.get_coords_x(event);
      var pickedObject = this.m_scenes.pick_object(x, y);
      if (pickedObject) {
        this.outlineOff();
        var _object = configuratorObject3d.getByObjectName(pickedObject.name);
        if (_object) {
          _object.pick();
          $rootScope.target = _object; 
          this.m_scenes.set_outline_color([0, 0.6, 1]);
          this.m_scenes.apply_outline_anim(pickedObject, 1.2, 1.2, 1);
          $scope.$emit('editModeOn', _object);
        }
      }
    };

    /**
     * @description
     * |En| Deactivate outline at all objects.
     * |Ru| Убираем подсветку у всех объектов.  
     */
    this.outlineOff = function () {
      var all = this.m_objects.get_outlining_objects();
      all.forEach(function (_object) {
        this.m_scenes.clear_outline_anim(_object);
      }.bind(this));
    };


   this.startPreloder = function (seconds) {
      var timeout = (seconds+2)/2 * 1000; 
      $rootScope.showPreloader = true;
      $timeout(function () {
        $rootScope.showPreloader = false;
      }, timeout);
    };

    if(this.export_wantenger == "true") {

    }
    else {
       this.init();
    }

    

    $scope.$on('startConfigurator3d', function () {
      priceService.getWantengerPrices();
      this.init();
    }.bind(this));

  }
}());
(function () {'use strict';

  /**
   * @description 
   * |En| Directive of edim mode.
   * |Ru| Директива режима редактирования.
   */
  angular.module('configuratorApp').directive('configuratorEditMode', configuratorEditMode);
  function configuratorEditMode () {
    return {
      restrict: 'E',
      // templateUrl: 'angularApp/directives/configuratorEditMode/configuratorEditMode.html',
      template: '<div class="edit-panel_container"><div class="edit-panel_container_edit-object"><div ng-style="{\'background-image\': \'url(\' + target.img + \')\'}" class="section-block_item_image_active"></div><div class="section-block_item_title_active">{{target.parent.title}}: {{target.title}} <div>Price: {{target.price}}</div></div></div><div ng-repeat="material in edit.materialNewArr track by $index" ng-if="target.isExcluded(material.name)"><div class="section-block_title" ng-bind="material.title"></div><div ng-if="target.isExcluded(item.name)" class="edit-panel_container_block-colors" ng-repeat="item in material.items track by $index" ng-style="{\'background-image\': \'url(\' + item.img + \')\', \'background-size\': \'cover\'}" ng-click="target.setMaterial(material.data.material_name, item.data.color)"><a ng-click="panel.download(item)"></a></div></div></div>',
      controller: 'configuratorEditModeController', controllerAs: 'edit'
    } 
  }

  angular.module('configuratorApp').controller('configuratorEditModeController', configuratorEditModeController);
  configuratorEditModeController.$inject = ['$http', '$rootScope', 'targetOfEdit', 'configuratorSection', 'b4wCanvas', 'priceService'];
  function configuratorEditModeController ($http, $rootScope, targetOfEdit, configuratorSection, b4wCanvas, priceService) {

    this.previewImg = b4wCanvas.previewImg;
    
    /**
     * @description 
     * |En| Target of edit
     * |Ru| Цель редактирования. 
     * @type {Object} target
     */
    $rootScope.target = targetOfEdit.target;
    
    /**
     * @description
     * |En| Collection of material.
     * |Ru| Коллекция материалов. 
     * @type {Array} materialNewArr
     */
    this.materialNewArr = configuratorSection.getMaterials();

  }

}());

(function () {'use strict';

  /**
   * @description 
   * |En| Directive of ZIP mode.
   * |Ru| Директива ZIP.
   */
  angular.module('configuratorApp').directive('configuratorZipMode', configuratorZipMode);
  function configuratorZipMode () {
    return {
      restrict: 'E',
      // templateUrl: 'angularApp/directives/configuratorEditMode/configuratorEditMode.html',
      template: '<div class="edit-panel_container"><div class="edit-panel_container_edit-object"><div ng-style="{\'background-image\': \'url(zip.png)\'}" class="section-block_item_image_active"></div><div class="section-block_item_title_active" ng-click="downloadClick()">Download zip</div></div><div ng-repeat="material in edit.materialNewArr track by $index" ng-if="target.isExcluded(material.name)"><div class="section-block_title" ng-bind="material.title"></div><div ng-if="target.isExcluded(item.name)" class="edit-panel_container_block-colors" ng-repeat="item in material.items track by $index" ng-style="{\'background-image\': \'url(\' + item.img + \')\', \'background-size\': \'cover\'}" ng-click="target.setMaterial(material.data.material_name, item.data.color)"></div></div></div>',
      controller: 'configuratorZipModeController', controllerAs: 'edit'
    } 
  }

  angular.module('configuratorApp').controller('configuratorZipModeController', configuratorZipModeController);
  configuratorZipModeController.$inject = ['$http','$scope', '$rootScope', 'targetOfEdit', 'configuratorSection', 'b4wCanvas', 'priceService','configuratorObject3d'];
  function configuratorZipModeController ($http,$scope, $rootScope, targetOfEdit, configuratorSection, b4wCanvas, priceService,configuratorObject3d) {

    $scope.downloadClick = function() {
      console.log('downloadClick')

    
  
      var materials = configuratorObject3d.getByType('material');
      var objectsAll = configuratorObject3d.getByTypeFilter('lamp');

     
      var zip = new JSZip();

      console.log('objectsAll',objectsAll)

      var _object1 = objectsAll[0];
      var _object2 = objectsAll[1];
      var _object3 = objectsAll[2];
    //    var _object4 = objectsAll[6];

     // materials.forEach(function (_object, key) { 
        zip.add(_object1.name+'.png', _object1.img.split('base64,')[1], {base64: true});
         zip.add(_object2.name+'.png', _object2.img.split('base64,')[1], {base64: true});
          zip.add(_object3.name+'.png', _object3.img.split('base64,')[1], {base64: true});
           //zip.add(_object4.name+'.png', _object4.img.split('base64,')[1], {base64: true});

     // })


      var content = zip.generate();

     
      location.href="data:application/zip;base64," + content; 

      //zip.folder("images").add("smile.gif", base64Data, {base64: true});

      //   
      // zip.add("S-1_top-1.png", "S-1_top-1.png");
      // zip.add("S-1_top-2.png", "S-1_top-2.png");
      // var content = zip.generate();
      // location.href="data:application/zip;base64," + content;

    }

   
  }

}());
(function () {'use strict';

  /**
   * @description 
   * |En| This main directive of application. All other components must located in this directive.
   * |Ru| Это главная директива приложения. Все другие компоненты приложения находятся внутри этой директивы.
   */
  angular.module('configuratorApp').directive('configuratorMain', configuratorMain);
  function configuratorMain () {
    return {
      restrict: 'E',
      // templateUrl: 'angularApp/directives/configuratorMain/configuratorMain.html',
      template: '<div class="preloader-img" ng-show="showPreloader"></div><configurator-canvas class="configurator-canvas"></configurator-canvas><configurator-panel class="configurator-panel"></configurator-panel><configurator-price></configurator-price>',
      controller: 'configuratorMainController', controllerAs: 'main'
    }
  }

  /**
   * @description 
   * |En| Controller of directive configuratorMain.
   * |Ru| Контроллек директвы configuratorMain.
   */
  angular.module('configuratorApp').controller('configuratorMainController', configuratorMainController);
  configuratorMainController.$inject = ["$rootScope"];
  function configuratorMainController ($rootScope) {
       $rootScope.showPreloader = true;
  }
  
}());
(function () {'use strict';

  /**
   * @description 
   * |En| Directive control panel of application.
   * |Ru| Директива панели управления приложением.
   */
  angular.module('configuratorApp').directive('configuratorPanel', configuratorPanel);
  function configuratorPanel () {
    return {
      restrict: 'E',
      // templateUrl: 'angularApp/directives/configuratorPanel/configuratorPanel.html',
      template: '<div class="panel"><div ng-if="panel.url || panel.zip" ng-click="panel.moveBack()" class="edit-panel_button-close"></div> <div ng-if="panel.url" class="edit-panel"><configurator-edit-mode></configurator-edit-mode></div> <div ng-if="panel.zip" class="edit-panel"><configurator-zip-mode></configurator-zip-mode></div> <div ng-repeat="section in panel.sections track by $index" class="section-block" ng-if="section.items.length && !panel.url && section.type !== \'material\'"><div class="section-block_title" ng-bind="section.title"></div><div class="section-block_items-wrapp"><div ng-repeat="item in section.items track by $index" class="section-block_item"><div ng-if="item.excluded" class="section-block_item_excluded"></div><ul ng-if="!item.excluded" ng-class="item.picked ? \'section-block_item-menu\' : \'section-block_item-menu_active\'" ><li ng-class="item.picked ? \'section-block_item-menu-pick_active\' : \'section-block_item-menu-pick\'" ng-click="item.pick()">{{item.picked ? \'Selected\' : \'Select\'}}</li><li class="section-block_item-menu-edit" ng-click="panel.editMode(item)" ng-if="item.picked">Edit</li><li class="section-block_item-menu-download" ng-click="panel.download(item)" >Download</li><li class="section-block_item-menu_price">Price: {{item.price}} {{price.priceService.currency}}</li></ul><div ng-style="{\'background-image\': \'url(\' + item.img + \')\'}" ng-class="item.picked ? \'section-block_item_image_active\' : \'section-block_item_image\'"></div><div ng-class="item.picked ? \'section-block_item_title_active\' : \'section-block_item_title\'" ng-bind="item.title"></div></div></div></div></div>',
      controller: 'configuratorPanelController', controllerAs: 'panel'
    } 
  }

  /**
   * @description 
   * |En| Controller of directive configuratorPanel.
   * |Ru| Контроллер директивы configuratorPanel.
   */
  angular.module('configuratorApp').controller('configuratorPanelController', configuratorPanelController);
  configuratorPanelController.$inject = ['$scope','$rootScope','$timeout', '$http', 'configuratorSection', 'targetOfEdit', 'b4wCanvas', 'priceService','configuratorObject3d'];
  function configuratorPanelController ($scope,$rootScope,$timeout, $http, configuratorSection, targetOfEdit, b4wCanvas, priceService,configuratorObject3d) {


     this.startPreloder = function (seconds) {
    var timeout = (seconds+2)/2 * 1000; 
    $rootScope.showPreloader = true;
    $timeout(function () {
      $rootScope.showPreloader = false;
    }, timeout);
  };


       $scope.makeScreens= function () { //, base64Data, {base64: true}
      // var zip = new JSZip();
      // zip.add("S-1_top-1.png", "S-1_top-1.png");
      // zip.add("S-1_top-2.png", "S-1_top-2.png");
      // var content = zip.generate();
      // location.href="data:application/zip;base64," + content;
      var delaultObjects = configuratorObject3d.getAllPicked();
      b4wCanvas.hideDefault(delaultObjects);

      b4wCanvas.m_container.resize(100, 100,true)

      var cnvs = b4wCanvas.m_container.get_canvas()
      cnvs.style.width = '100px';
      cnvs.style.height = '100px';
      
      console.log('cnvs',cnvs)

      var _this = this;
       $timeout(function () {

      //_this.runZipMode()


      var materials = configuratorObject3d.getByType('material');
      _this.startPreloder(materials.length+13);
      
      console.log('materials',materials)

      materials.forEach(function (_object, key) {
       // if(!_object.user_image) {
        _object.getPreviewImg(key + 10);
        //}
      });

      var objects = configuratorObject3d.getByTypeFilter('material');

      console.log('objects',objects)
      var baseObject = objects.filter(function(e) {
        return e.name == "base"
      })[0]

        objects.forEach(function (_object, key) {
         // if(!_object.user_image) {
        _object.getPreviewImgObjects(baseObject,key + 1);
          //}
      });

        },1000)
  

        //$scope.$digest()
    }.bind(this);

    /**
     * @property {String|null} url Ссылка на html-файл.
     */
    this.url = null;

    /**
     * @property {Boolean} zip Enable zip mode;
     */
    this.zip = false;

    /**
     * @property {Array} sections
     */
    this.sections = configuratorSection.getAll();

    /**
     * @description
     * |En| Event listner on open panel of edit mode. 
     * |Ru| Слушатель события на открытие панели редактирования объекта.
     */
    $scope.$on('editModeOn', function (event, _object) {
      targetOfEdit.target = _object;
      this.setMode('edit');
      $scope.$digest();
    }.bind(this));


    this.runZipMode = function () {
      this.zip = true;
    };

    /**
     * @description 
     * |En| Activate mode of change material.
     * |Ru| Активируем режим выбора материала.
     * @param {String} modeName
     */
    this.setMode = function (modeName) {
      this.url = 'angularApp/directives/configuratorPanel/configuratorPanel-' + modeName + '.html'
    };

    /**
     * @description 
     * |En| Callback of button (Close). Close extra panel.
     * |Ru| Колбэк кнопки (Закрыть). Закрывает дополнительную панель.
     */
    this.moveBack = function () {
      this.url = null;
      this.zip = false;
    };

    /**
     * @description
     * |En| Opening panel of config color and material of 3d-object.
     * |Ru| Открываем панель настройки цвета и материала 3д-объекта.
     * @param  {Object} object3d 
     */
    this.editMode = function (object3d) {
      targetOfEdit.target = object3d;
      this.setMode('edit');
    };

      this.download = function (object3d) {
      console.log('object3d',object3d)
        download(object3d.img, object3d.name+".png",  "image/png");

    };

  }

}());
(function () {'use strict';
  
  angular.module('configuratorApp').directive('configuratorPrice', configuratorPrice);
  function configuratorPrice () {
    return {
      restirct: 'E',
      // templateUrl: 'angularApp/directives/configuratorPrice/configuratorPrice.html',
      template: '<div class="panel_price-menu" ><span  class="price_tag">Price {{price.priceService.currentPrice}} {{price.priceService.currency}}</span><span ng-click="makeScreens()" class="make_screens">Make screenshots</span></div><div class="order-form" ng-if="showPopup"><ul class="order-form_wrapp"><li><span>Ф.И.О:</span> <input type="text" placeholder="Иванов Иван Иванович" ng-focus="cameraOff()" ng-blur="cameraOn()"></li><li><span>Email:</span> <input type="text" placeholder="mail@mail.ru" ng-focus="cameraOff()" ng-blur="cameraOn()"></li><li><span>Телефон:</span> <input type="text" placeholder="+7 (495) 777 11 22" ng-focus="cameraOff()" ng-blur="cameraOn()"></li><li><span>Номер карты:</span> <input type="text" placeholder="1234 5678 9012 3456" ng-focus="cameraOff()" ng-blur="cameraOn()"></li><li><div class="order-form_button" ng-click="showForm()">Купить</div></li></ul></div>',
      controller: 'configuratorPriceController', controllerAs: 'price'
    }
  }

  angular.module('configuratorApp').controller('configuratorPriceController', configuratorPriceController);
  configuratorPriceController.$inject = ['$scope', 'priceService', 'b4wCanvas','configuratorObject3d'];
  function configuratorPriceController ($scope, priceService, b4wCanvas,configuratorObject3d) {
    this.priceService = priceService;

    $scope.showPopup = false;

    $scope.showForm = function () {
      $scope.showPopup ? $scope.showPopup = false : $scope.showPopup = true;
    };

 


    /**
     * @description
     * Отключаем управление камерой в момент ввода значений в инпут
     */
    $scope.cameraOff = function () {
      b4wCanvas.cameraControlOff();
    };

    /**
     * @description 
     * Включаем управление камерой в момент ввода значений в инпут
     */
    $scope.cameraOn = function () {
      b4wCanvas.cameraControlOn();
    };
  }

}());