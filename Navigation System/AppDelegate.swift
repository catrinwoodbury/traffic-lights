//
//  AppDelegate.swift
//  Navigation System
//
//  Created by Woodbury Catrin on 3/28/24.
//

import Foundation
import UIKit
import GoogleMaps

class AppDelegate: NSObject, UIApplicationDelegate {
    
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {
        GMSServices.provideAPIKey("AIzaSyCqhq6c811qavWvjC3vpEVuoZcZtcJO_0Q")
        return true
    }
}
