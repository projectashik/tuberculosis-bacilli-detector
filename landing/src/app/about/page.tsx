const AboutPage = () => {
  return (
    <div className='min-h-screen bg-white'>
      {/* Main Content */}
      <div className='max-w-6xl mx-auto px-4 py-12'>
        <h2 className='text-3xl font-bold text-gray-800 mb-6'>
          About CellSight
        </h2>
        <p className='text-lg text-gray-600 mb-12'>
          CellSight represents the future of microscopic analysis, combining
          precision engineering with cutting-edge automation technology. Our
          innovative system transforms traditional microscopy into an efficient,
          automated process that delivers consistent, reliable results while
          saving valuable time and resources.
        </p>

        {/* Feature Cards */}
        <div className='grid md:grid-cols-3 gap-8 mb-16'>
          <div className='bg-gray-50 p-6 rounded-lg shadow-md'>
            <h3 className='text-xl font-bold text-blue-600 mb-4'>
              Automated Excellence
            </h3>
            <p className='text-gray-600'>
              Our system features a motorized microscope stage that precisely
              moves samples, ensuring comprehensive coverage and consistent
              analysis. The automated workflow eliminates human error and
              fatigue, delivering reliable results 24/7.
            </p>
          </div>

          <div className='bg-gray-50 p-6 rounded-lg shadow-md'>
            <h3 className='text-xl font-bold text-blue-600 mb-4'>
              Advanced Imaging
            </h3>
            <p className='text-gray-600'>
              Equipped with a high-resolution camera module, CellSight captures
              detailed microscopic images every 3 seconds. These images provide
              the foundation for accurate analysis and diagnosis.
            </p>
          </div>

          <div className='bg-gray-50 p-6 rounded-lg shadow-md'>
            <h3 className='text-xl font-bold text-blue-600 mb-4'>
              Smart Processing
            </h3>
            <p className='text-gray-600'>
              Powered by Raspberry Pi technology, CellSight processes and stores
              images efficiently, creating an organized database of samples that
              can be accessed and analyzed at any time.
            </p>
          </div>
        </div>

        {/* Technical Specs */}
        <div className='bg-gray-50 p-8 rounded-lg mb-16'>
          <h2 className='text-2xl font-bold text-gray-800 mb-6'>
            Technical Innovation
          </h2>
          <p className='text-gray-600 mb-6'>
            CellSight leverages cloud technology through Azure Blob storage,
            enabling secure and organized storage of patient data. Each sample
            is meticulously cataloged under unique patient IDs, ensuring data
            integrity and easy retrieval.
          </p>

          <h3 className='text-xl font-bold text-gray-800 mb-4'>
            Key Features:
          </h3>
          <ul className='list-disc pl-6 text-gray-600 space-y-2'>
            <li>Real-time image capture every 3 seconds</li>
            <li>Motorized sample movement for precise analysis</li>
            <li>Integrated camera module for high-quality imaging</li>
            <li>Raspberry Pi-powered processing</li>
            <li>Secure cloud storage with Azure Blob</li>
            <li>Patient-specific data organization</li>
          </ul>
        </div>

        {/* Vision Section */}
        <div className='mb-12'>
          <h2 className='text-2xl font-bold text-gray-800 mb-6'>Our Vision</h2>
          <p className='text-gray-600 mb-6'>
            At CellSight, we&apos;re committed to advancing healthcare through
            technology. Our automated microscopic sampling testing device is
            just the beginning of our journey to revolutionize medical
            diagnostics and research. By combining precision engineering with
            innovative software solutions, we&apos;re creating tools that enable
            healthcare professionals to work more efficiently and effectively.
          </p>

          <p className='text-gray-600'>
            Join us in shaping the future of microscopic analysis at{" "}
            <a
              href='https://cellsight.co'
              className='text-blue-600 hover:text-blue-800'
            >
              cellsight.co
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}

export default AboutPage
