import UIKit

class HelloWorldViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        
        let label = UILabel(frame: CGRect(x: 0, y: 0, width: 300, height: 50))
        label.center = view.center
        label.textAlignment = .center
        label.text = "Hello, World!"
        
        view.addSubview(label)
    }
}

// This would typically be in the AppDelegate.swift file
@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {
    var window: UIWindow?
    
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        window = UIWindow(frame: UIScreen.main.bounds)
        window?.rootViewController = HelloWorldViewController()
        window?.makeKeyAndVisible()
        return true
    }
}
